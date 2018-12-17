# -*- coding: utf-8 -*-
"""
pytest-testlink-adaptor
***********************
"""


from __future__ import print_function
import os
import sys
import re
from collections import defaultdict

from path import Path
import pytest

import testlink
from testlink import TestLinkError


if sys.version_info[0] < 3:
    import ConfigParser as configparser

    configparser.ConfigParser = configparser.SafeConfigParser
else:
    import configparser


PLUGIN_NAME = "pytest-testlink-adaptor"


# pylint: disable=R0903
class TLINK(object):
    """
    Class for storing basic TestLink configurations and RPC handler
    """
    # globals
    enabled = True
    exit_on_fail = False
    ini = configparser.ConfigParser()
    ini_required_keys = ['xmlrpc_url', 'api_key', 'project', 'test_plan',
                         'build_name']
    ini_optional = ['new_build', 'reference_test_plan', 'custom_field']
    nodes = defaultdict(list)
    maps = {}
    conf = {}

    rpc = testlink.TestlinkAPIClient
    testplan_platforms = None
    testplanid = None

    def __init__(self):
        pass

    def __str__(self):
        return PLUGIN_NAME

    def __repr__(self):
        return PLUGIN_NAME

    @classmethod
    def disable_or_exit(cls, err_msg):
        """
        Disables Testlink reporting ability
        :param err_msg: error message to display
        """
        print('testlink: disabled! %s' % err_msg)
        cls.enabled = False
        if cls.exit_on_fail:
            raise TestLinkError(err_msg)


###############################################################################
# ini file processing
###############################################################################
def load_testlink_file(file_path):
    """
    Loads testlink configuration file
    :param file_path: path to Testlink config file
    """
    if not file_path.isfile():
        print("ERROR: testlink_file not found!")
        TLINK.disable_or_exit('FileNotFoundError: testlink_file: %s'
                              % file_path)
    if not TLINK.enabled:
        return

    # read ini file
    TLINK.ini.read(file_path)

    # load testlink-conf section
    if 'testlink-conf' in TLINK.ini.sections():
        TLINK.conf = {}
        for param_name, param_val in TLINK.ini.items('testlink-conf'):
            if param_val.strip().startswith('$'):
                param_val = os.environ[param_val.strip()[1:]]
            else:
                param_val = param_val.strip()
            TLINK.conf[param_name] = param_val

        missing_tl_keys = set(TLINK.ini_required_keys) - set(TLINK.conf)

        if missing_tl_keys:
            TLINK.disable_or_exit('Missing testlink ini keys:'
                                  ' %s' % list(missing_tl_keys))

    else:
        TLINK.disable_or_exit('section "testlink-conf" not found in ini file:'
                              ' %s' % file_path)

    # load testlink-maps section
    if 'testlink-maps' in TLINK.ini.sections():
        # TLINK.maps = TLINK.ini._sections['testlink-maps']
        TLINK.maps = {item: value for item, value
                      in TLINK.ini.items('testlink-maps')}

    else:
        print('section "testlink-maps" not found in ini file: %s' % file_path)


def load_conf_section():
    """
    Loads section of the config file
    """
    def process_config_env_value(key):
        """Returns value of config key"""
        if TLINK.conf[key].strip().startswith('$'):
            return os.environ[TLINK.conf[key][1:]]
        return TLINK.conf[key]

    missing_tl_keys = {k for k in TLINK.ini_required_keys
                       if k not in TLINK.conf}
    if missing_tl_keys:
        TLINK.disable_or_exit('Missing testlink ini keys:'
                              ' %s' % missing_tl_keys)
    else:
        for conf_key in TLINK.conf:
            TLINK.conf[conf_key] = process_config_env_value(conf_key)


def load_maps_section():
    """
    Loads tc mapping from testlink config files
    """
    node_dict = defaultdict(list)
    for key, val in TLINK.maps.items():
        node_dict[val].append(key)
    duplicates = [x for x in node_dict if len(node_dict[x]) != 1]
    if duplicates:
        TLINK.disable_or_exit('Duplicate node ids in testlink maps: %s'
                              % duplicates)
        return
    # construct the nodes dict
    TLINK.nodes = {v: k for k, v in TLINK.maps.items()}


###############################################################################
# test link section
###############################################################################

def init_testlink():
    """Test link initialization"""
    if not TLINK.enabled:
        return
    # connect to test link
    TLINK.rpc = testlink.TestlinkAPIClient(server_url=TLINK.conf['xmlrpc_url'],
                                           devKey=TLINK.conf['api_key'])

    # assert test project exists
    _test_project = TLINK.rpc.getTestProjectByName(TLINK.conf['project'])
    if not _test_project:
        TLINK.disable_or_exit(
            'Invalid tl_project name. Unable to find project')
        return

    # type convert from list for older testlink instances
    _test_project = _test_project[0] \
        if isinstance(_test_project, list) else _test_project

    # get project id and prefix
    TLINK.project_id = _test_project['id']
    TLINK.project_prefix = _test_project['prefix']

    # create test plan if required
    plan_name = [tp for tp in TLINK.rpc.getProjectTestPlans(TLINK.project_id)
                 if tp['name'] == TLINK.conf['test_plan']]
    if not plan_name:
        # pylint: disable=E1121
        TLINK.rpc.createTestPlan(TLINK.conf['test_plan'],
                                 TLINK.conf['project'])
        plan_name = [tp for tp in
                     TLINK.rpc.getProjectTestPlans(TLINK.project_id) if
                     tp['name'] == TLINK.conf['test_plan']]
    TLINK.test_plan_id = plan_name[0]['id']

    TLINK.test_build_id = None
    TLINK.test_platform = None

    TLINK.tc_pattern = re.compile(r'%s\d+' % TLINK.conf['pytest_tc_prefix'],
                                  re.I)


###############################################################################
# py test hooks
###############################################################################
def pytest_addoption(parser):
    """Add all the required ini and command line options here"""
    parser.addoption(
        '--no-testlink', action="store_false", dest="testlink", default=True,
        help="disable pytest-testlink"
    )
    parser.addoption(
        '--testlink-exit-on-error', action="store_true",
        dest="testlink_exit_on_fail", default=False,
        help="exit on any test link plugin related errors/exceptions"
    )
    parser.addini('testlink_file', 'Location of testlink configuration'
                                   ' ini file.')


def pytest_configure(config):
    """
    Configures Testlink parameters according to config file
    :param config: testlink section in pytest config
    :return:
    """
    if not config.option.testlink:
        TLINK.enabled = False
        return
    if 'testlink_file' not in config.inicfg:
        TLINK.enabled = False
        return

    if config.option.testlink_exit_on_fail:
        TLINK.exit_on_fail = True

    # load testlink-conf section
    load_testlink_file(Path(config.inicfg['testlink_file']))
    if not TLINK.enabled:
        return

    load_conf_section()
    if not TLINK.enabled:
        return

    load_maps_section()
    if not TLINK.nodes:
        TLINK.disable_or_exit("No nodes found!")
        return

    init_testlink()


def pytest_report_header(config):
    """ pytest report hook"""
    if not config.option.testlink:
        print('testlink: disabled by --no-testlink')
    elif 'testlink_file' in config.inicfg:
        print('testlink: %s' % config.inicfg['testlink_file'])
    else:
        print(
            'testlink: "testlink_file" key was not found in [pytest] section')

    if config.option.testlink_exit_on_fail:
        print('testlink: exit on failure enabled!')


def pytest_runtest_logreport(report):
    """
    Main pytest hook for reporting test results in Testlink
    :param report: pytest report results object
    :return:
    """
    if not TLINK.enabled:
        return

    status = ''
    if report.passed:
        # ignore setup/teardown
        if report.when == "call":
            status = 'p'
    elif report.failed:
        status = 'f'
    elif report.skipped:
        status = 'b'
    if status:
        if not getattr(TLINK, 'test_build_id'):
            set_build()

        test_name = report.nodeid.split('::')[-1]
        report_result(test_name=test_name, status=status,
                      duration=report.duration,
                      build=TLINK.test_build_id, platform=TLINK.test_platform)

###############################################################################
# common tools
###############################################################################


def set_build():
    """ Sets test_build_id and test_platform attributes
        from approprirate pytest attributes or environment variables in
        this priority:
         1. pytest attribute
         2. environment variable
         3. testlink.ini config
    """

    build_name = getattr(
        pytest, 'prod_vers', None) or os.environ.get(
            'PROD_VERS') or TLINK.conf.get('prod_vers')

    prod_platform = getattr(
        pytest, 'prod_platform', None) or os.environ.get(
            'PROD_PLATFORM') or TLINK.conf.get('prod_platform')

    print('product build: {}'.format(build_name))
    print('product platform: {}'.format(prod_platform))

    if not build_name:
        msg = '!!! no one of pytest prod_vers attribute,' \
              ' environment variable PROD_VERS,' \
              ' build_name parameter from testlink.ini is not set!' \
              ' Testlink reporting will be disabled'
        print(msg)
        TLINK.disable_or_exit(err_msg=msg)
        return

    if not prod_platform:
        msg = '!!! prod_platform is not set!' \
              ' Testlink reporting will be disabled'
        print(msg)
        TLINK.disable_or_exit(err_msg=msg)
        return

    TLINK.test_platform = prod_platform

    # get platforms of testplan

    # (no-value-for-parameter)
    # pylint: disable=E1120
    # (unexpected - keyword - arg)
    # pylint: disable=E1123
    TLINK.testplan_platforms = TLINK.rpc.getTestPlanPlatforms(
        testplanid=TLINK.test_plan_id)

    TLINK.test_platform_id = [x['id'] for x in TLINK.testplan_platforms if
                              x['name'] == TLINK.test_platform][0]

    # create test build if required
    TLINK.test_build = [tb for tb in
                        TLINK.rpc.getBuildsForTestPlan(TLINK.test_plan_id)
                        if tb['name'] == build_name]
    if not TLINK.test_build:
        # pylint: disable=E1121
        TLINK.rpc.createBuild(int(TLINK.test_plan_id), build_name,
                              'Automated test. Created by testlink plugin.')
        TLINK.test_build = [tb for tb in
                            TLINK.rpc.getBuildsForTestPlan(TLINK.test_plan_id)
                            if tb['name'] == build_name]
    TLINK.test_build_id = TLINK.test_build[0]['id']


def testlink_configure(config, exit_on_fail=False):
    """
    Configures Testlink parameters according to config file
    :param config: testlink section in pytest config
    :return:
    """

    TLINK.exit_on_fail = exit_on_fail

    # load testlink-conf section
    load_testlink_file(Path(config))
    if not TLINK.enabled:
        return

    load_maps_section()
    if not TLINK.nodes:
        TLINK.disable_or_exit("No nodes found!")
        return

    init_testlink()


def report_result(test_name, status, duration, build=None, platform=None):
    """
     Stores results in Testlink
    :param test_name:
    :param build:
    :param status: 'p' - passed, 'f' - failed, 'b' - skipped
    :param duration: test duration in seconds
    :param platform: name of platform
    """

    build_id = build or TLINK.test_build_id
    platform_name = platform or TLINK.test_platform

    if not TLINK.enabled:
        return

    if status:
        try:
            # try to find tc id in test name
            res = TLINK.tc_pattern.search(test_name)
            if res:
                test_id = res.group(0)
            else:
                # check for id mapping in testlink.ini
                if test_name in TLINK.nodes:
                    test_id = TLINK.nodes[test_name]
                else:
                    print('testlink: WARN: ext-id not found: %s'
                          % test_name)
                    return

            # change testcase prefix
            # Pytest specific
            # (no-value-for-parameter)
            # pylint: disable=E1120
            # (unexpected - keyword - arg)
            # pylint: disable=E1123
            if test_id.startswith(TLINK.conf['pytest_tc_prefix']):
                test_id = '{0}{1}'\
                    .format(TLINK.conf['testlink_tc_prefix'],
                            test_id[len(TLINK.conf['pytest_tc_prefix']):])

            # get available test info
            tc_info = TLINK.rpc.getTestCase(testcaseexternalid=test_id)[0]
            tc_version = int(tc_info['version'])
            tc_id = tc_info['testcase_id']

            # get existing attached platforms.
            # attached_versions: dict with testcase info
            #  and platform_id as a key
            attached_versions = TLINK.rpc.getTestCasesForTestPlan(
                testplanid=TLINK.test_plan_id, testcaseid=tc_id)[tc_id]

            # add test case to tesplan if needed
            if TLINK.test_platform_id not in attached_versions:
                TLINK.rpc.addTestCaseToTestPlan(
                    testprojectid=TLINK.project_id,
                    testplanid=TLINK.test_plan_id, testcaseexternalid=test_id,
                    version=tc_version, platformid=TLINK.test_platform_id)

            print(TLINK.rpc.reportTCResult(testplanid=TLINK.test_plan_id,
                                           buildid=build_id,
                                           platformname=platform_name,
                                           status=status,
                                           testcaseexternalid=test_id,
                                           user=TLINK.conf['tester'],
                                           execduration='%.2f'
                                           % round(duration/60, 2)))
            print(test_id)

        except TestLinkError as exc:
            print('testlink: WARN: Unable to update'
                  ' result: %s' % test_name)
            print('testlink: Check if the test case is not linked'
                  ' to test plan!')
            print(exc.message.encode('utf8'))


if __name__ == '__main__':
    testlink_configure(
        '/media/sf_virt_share/qa_host_tools/pana_git_back/'
        'host_tools_1121/qa-tools/tests/testlink.ini')
