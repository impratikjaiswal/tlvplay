import os

from python_helpers.ph_constants import PhConstants
from python_helpers.ph_dos import PhDos
from python_helpers.ph_keys import PhKeys
from python_helpers.ph_process import PhProcess
from python_helpers.ph_util import PhUtil

from tlv_play.test.test_data import TestData


class TestAutoBatch:
    BATCH_RUN_TC = 'run_tc_tlv_play.bat'

    MODULE_NAME = 'tlv_play.main.tlvplay'

    PROJECT_PATH = r'D:\Other\Github_Self\tlvPlay'

    get_file_path_mapping_relative = {
        PhKeys.VAR_EXECUTION_MODE: r'tlv_play\main\tlvplay.py',
        PhKeys.VAR_ERROR_HANDLING_MODE: r'tlv_play\main\tlvplay.py',
        PhKeys.VAR_TOP_FOLDER_PATH: r'tlv_play\main\helper\folders.py',
    }

    get_target_str = {
        PhKeys.VAR_EXECUTION_MODE: 'execution_mode = PhExecutionModes.',
        PhKeys.VAR_ERROR_HANDLING_MODE: 'error_handling_mode = PhErrorHandlingModes.',
        PhKeys.VAR_TOP_FOLDER_PATH: 'top_folder_path = ',
    }

    @classmethod
    def _update_variables_in_file(cls, test_case_data):

        def __update_variable_in_file(_target_file, _target_str, _target_value):
            update_available = False
            current_value = None
            if PhUtil.is_empty(_target_file):
                return None
            if PhUtil.is_empty(_target_str):
                return None
            if PhUtil.is_empty(_target_value):
                return None
            with open(_target_file) as f_read:
                file_data = f_read.read().split('\n')
            for index, item in enumerate(file_data):
                if _target_str in item:
                    item_data = item.split(_target_str)
                    if len(item_data) > 1:
                        current_value = item_data[1]
                        if PhUtil.is_not_empty(current_value) and _target_value != current_value:
                            update_available = True
                            item_data[1] = _target_value
                        if update_available:
                            file_data[index] = _target_str.join(item_data)
                        break
            if update_available:
                with open(_target_file, 'w') as f_write:
                    f_write.writelines('\n'.join(file_data))
                return current_value
            return None

        original_data = {}
        target_keys = [
            PhKeys.VAR_EXECUTION_MODE,
            PhKeys.VAR_ERROR_HANDLING_MODE,
            PhKeys.VAR_TOP_FOLDER_PATH,
        ]
        for target_key in target_keys:
            if target_key not in test_case_data:
                continue
            target_str = TestAutoBatch.get_target_str.get(target_key)
            target_value = test_case_data.get(target_key)
            target_file = os.sep.join(
                [TestAutoBatch.PROJECT_PATH, TestAutoBatch.get_file_path_mapping_relative.get(target_key)])
            value_original = __update_variable_in_file(target_file, target_str, target_value)
            if value_original is not None:
                print(f'{target_key}: value_original was {value_original}; target_value is {target_value}')
                original_data.update({target_key: value_original})
        return original_data

    @classmethod
    def clean_up(cls, original_data):
        cls._update_variables_in_file(original_data)

    @classmethod
    def prepare_batch_file(cls, test_case_data):
        """

        :param test_case_data:
        :return:
        """
        executable_script = [
            '@echo off',
            PhDos.switch_to_current_folder(),
            PhDos.get_seperator(test_case_data.get(PhKeys.TEST_CASE_ID)),
            PhDos.change_directory_parent(),
            PhDos.change_directory_parent()
        ]
        executable_script.extend(PhDos.call_script_for_env_handling(True))
        log_file_path = os.sep.join(['tlv_play', 'test', 'logs', test_case_data.get(PhKeys.TEST_CASE_FILE_NAME)])
        executable_script.append(
            f'{PhDos.run_python(module_name=TestAutoBatch.MODULE_NAME)}'
            f'{PhConstants.SEPERATOR_TWO_WORDS}'
            f'{PhDos.redirect_output(file_path=log_file_path)}',
        )
        executable_script.extend(PhDos.call_script_for_env_handling(False))
        executable_script.append(PhDos.get_seperator(heading="Batch Execution Done"))
        batch_file_path = os.sep.join([TestAutoBatch.BATCH_RUN_TC])
        with open(batch_file_path, mode='w') as my_file:
            my_file.write('\n'.join(executable_script))
        PhProcess.run_batch_file(batch_file_path)

    @classmethod
    def test(cls, test_case_data):
        """

        :param test_case_data:
        :return:
        """
        PhUtil.print_heading(test_case_data.get(PhKeys.TEST_CASE_ID))
        PhUtil.print_iter(test_case_data, header='test_case_data')
        PhUtil.print_heading('update_variables_in_file', heading_level=2)
        original_data = cls._update_variables_in_file(test_case_data)
        cls.prepare_batch_file(test_case_data)
        PhUtil.print_heading('clean_up', heading_level=2)
        cls.clean_up(original_data)

    @classmethod
    def test_all(cls):
        """

        :return:
        """
        test_cases_data_pool = [
            # Unit Testing Sequences
            TestData.get_test_data('user'),
            TestData.get_test_data('sample_list'),
            TestData.get_test_data('dev'),
            TestData.get_test_data('unit_testing_external'),
            TestData.get_test_data('all'),
        ]
        for test_case_data in test_cases_data_pool:
            cls.test(test_case_data)


def main():
    TestAutoBatch.test_all()


if __name__ == '__main__':
    main()