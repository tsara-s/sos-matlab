#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

from sos_notebook.test_utils import NotebookTest
import random


class TestOctaveDataExchange(NotebookTest):

    def _var_name(self):
        if not hasattr(self, '_var_idx'):
            self._var_idx = 0
        self._var_idx += 1
        return f'var{self._var_idx}'

    def get_from_SoS(self, notebook, sos_expr):
        var_name = self._var_name()
        notebook.call(f'{var_name} = {sos_expr}', kernel='SoS')
        return notebook.check_output(
            f'''\
            %get {var_name}
            disp({var_name})
            ''',
            kernel='Octave')

    def put_to_SoS(self, notebook, py2_expr):
        var_name = self._var_name()
        notebook.call(
            f'''\
            %put {var_name}
            {var_name} = {py2_expr}
            ''',
            kernel='Octave')
        return notebook.check_output(f'print(repr({var_name}))', kernel='SoS')

    def test_get_none(self, notebook):
        assert 'NaN' == self.get_from_SoS(notebook, 'None')

    def test_put_NaN(self, notebook):
        assert 'None' == self.put_to_SoS(notebook, 'NaN')

    def test_get_int(self, notebook):
        assert 123 == int(self.get_from_SoS(notebook, '123'))
        assert '1.2346e+12' == self.get_from_SoS(notebook, '1234567891234')

    def test_put_int(self, notebook):
        assert 123 == int(self.put_to_SoS(notebook, '123'))
        assert 1234567891234 == int(self.put_to_SoS(notebook, '1234567891234'))
        # rounding error occurs
        assert 123456789123456784 == int(
            self.put_to_SoS(notebook, '123456789123456789'))

    def test_get_double(self, notebook):
        val = str(random.random())
        assert abs(float(val) - float(self.get_from_SoS(notebook, val))) < 1e-10

    def test_put_double(self, notebook):
        val = str(random.random())
        assert abs(float(val) - float(self.put_to_SoS(notebook, val))) < 1e-10

    def test_get_logic(self, notebook):
        assert '1' == self.get_from_SoS(notebook, 'True')
        assert '0' == self.get_from_SoS(notebook, 'False')

    def test_put_logic(self, notebook):
        assert 'True' == self.put_to_SoS(notebook, 'true')
        assert 'False' == self.put_to_SoS(notebook, 'false')

    def test_get_num_array(self, notebook):
        assert '[1]' == self.get_from_SoS(notebook, '[1]')
        assert '[1, 2]' == self.get_from_SoS(notebook, '[1, 2]')
        #
        assert '[1.23]' == self.get_from_SoS(notebook, '[1.23]')
        assert '[1.4, 2]' == self.get_from_SoS(notebook, '[1.4, 2]')

    def test_get_numpy_array(self, notebook):
        notebook.call('import numpy as np', kernel='SoS')
        assert '[1 2 3]' == self.get_from_SoS(notebook, 'np.array([1, 2, 3])')

    def test_put_num_array(self, notebook):
        # Note that single element numeric array is treated as single value
        assert '[1]' == self.put_to_SoS(notebook, '[1]')
        assert '[1, 2]' == self.put_to_SoS(notebook, '[1, 2]')
        #
        assert '[1.23]' == self.put_to_SoS(notebook, '[1.23]')
        assert '[1.4, 2]' == self.put_to_SoS(notebook, '[1.4, 2]')

    def test_get_logic_array(self, notebook):
        assert '[True]' == self.get_from_SoS(notebook, '[True]')
        assert '[True, False, True]' == self.get_from_SoS(
            notebook, '[True, False, True]')

    def test_put_logic_array(self, notebook):
        # Note that single element numeric array is treated as single value
        assert '[True]' == self.put_to_SoS(notebook, '[True]')
        assert '[True, False, True]' == self.put_to_SoS(notebook,
                                                        '[True, False, True]')

    def test_get_str(self, notebook):
        assert "u'ab c d'" == self.get_from_SoS(notebook, "'ab c d'")
        assert "u'ab\\td'" == self.get_from_SoS(notebook, r"'ab\td'")

    def test_put_str(self, notebook):
        assert "'ab c d'" == self.put_to_SoS(notebook, "'ab c d'")
        assert "'ab\\td'" == self.put_to_SoS(notebook, r"'ab\td'")

    def test_put_char_array(self, notebook):
        output = self.put_to_SoS(notebook, "['1'; '2'; '3']")

    def test_get_mixed_list(self, notebook):
        assert "[1.4, True, u'asd']" == self.get_from_SoS(
            notebook, '[1.4, True, "asd"]')

    def test_put_mixed_list(self, notebook):
        # R does not have mixed list, it just convert everything to string.
        assert "[1.4, True, 'asd']" == self.put_to_SoS(notebook,
                                                       '[1.4, True, "asd"]')

    def test_get_dict(self, notebook):
        output = self.get_from_SoS(notebook, "dict(a=1, b='2')")
        assert "{u'a': 1, u'b': u'2'}" == output or "{u'b': u'2', u'a': 1}" == output

    def test_put_dict(self, notebook):
        output = self.put_to_SoS(notebook, "dict(a=1, b='2')")
        assert "{'a': 1, 'b': '2'}" == output or "{'b': '2', 'a': 1}" == output

    def test_get_set(self, notebook):
        output = self.get_from_SoS(notebook, "{1.5, 'abc'}")
        assert "set([1.5, u'abc'])" == output or "set([u'abc', 1.5])" == output

    def test_get_complex(self, notebook):
        assert "(1+2.2j)" == self.get_from_SoS(notebook, "complex(1, 2.2)")

    def test_put_complex(self, notebook):
        assert "(1+2.2j)" == self.put_to_SoS(notebook, "complex(1, 2.2)")

    def test_get_recursive(self, notebook):
        output = self.get_from_SoS(notebook,
                                   "{'a': 1, 'b': {'c': 3, 'd': 'whatever'}}")
        assert "u'a': 1" in output and "u'b':" in output and "u'c': 3" in output and "u'd': u'whatever'" in output

    def test_put_recursive(self, notebook):
        output = self.put_to_SoS(notebook,
                                 "{'a': 1, 'b': {'c': 3, 'd': 'whatever'}}")
        assert "'a': 1" in output and "'b':" in output and "'c': 3" in output and "'d': 'whatever'" in output

    def test_get_matrix(self, notebook):
        notebook.call('import numpy as np', kernel='SoS')
        output = self.get_from_SoS(notebook, 'np.matrix([[1,2],[3,4]])')

    def test_put_matrix(self, notebook):
        output = self.put_to_SoS(notebook, '[1:3; 2:4]')

    def test_get_dataframe(self, notebook):
        notebook.call('''
            %put df --to Octave
            import pandas as pd
            import numpy as np
            import scipy.io as sio
            arr = np.random.randn(1000)
            arr[::10] = np.nan
            df = pd.DataFrame({'column_{0}'.format(i): arr for i in range(10)})
            ''', kernel='SoS')
        assert '900 10' in notebook.get_output('display(size(df))')
        #
        #  non-numeric dataframe
        notebook.call('''
            %put df --to Octave
            import pandas as pd

            df = pd.DataFrame({'name': ['Leonardo', 'Donatello', 'Michelangelo', 'Raphael'],
                   'mask': ['blue', 'purple', 'orange', 'red'],
                   'weapon': ['ninjatos', 'bo', 'nunchaku', 'sai']})
            ''', kernel='SoS')
        assert '900 10' in notebook.get_output('display(size(df))')
