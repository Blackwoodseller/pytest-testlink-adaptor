pytest-testlink-adaptor
=======================


Allow to update test results in Testlink TMS.

Uses testlink.ini file with test case id and test node id as mapping:
Every parameter value can be hardcoded or defined via environment variable
(e.g. test_plan=$TESTPLAN)

### Testlink file format (testlink.ini)
    [testlink-conf]
    xmlrpc_url=http://[test link server]/testlink/lib/api/xmlrpc.php
    api_key=<api_key> (can be generated in Testlink->My Settings->API interface->Generate Key)
    project=<Project name in TestLink>
    
    # prefix for testcases in TestLink project
    testlink_tc_prefix=TC-
    
    # pytest_tc_prefix [optional parameter]
    # name of pytest test function/method can contain testcase id in format <pytest_tc_prefix><case_number>.
    # for mapping with TestLink test cases.
    # If this parameter is omitted or is not matched the plugin
    # will try to collate test using mapping from testlink-maps section
    pytest_tc_prefix=TC  
               
    # Test plan in TestLink for specified project.
    # If the test case is not assigned to the test plan it will be assigned
    # automatically     
    test_plan=$TESTPLAN
    
    build_name=autobuild
    tester=<tester_name> (tester name in Testlink for automatic execution)
    exit_on_fail=optional [False by default]

    new_build=optional [False by default] (with True will create a new build)

    # prod_vers - product version
    # can be set via plugin parameter, pytest attribute or environment variable
    prod_vers=$PROD_VERS
    
    # prod_platform - product test platform in the Testlink test plan
    # can be set via plugin parameter, pytest attribute or environment variable
    prod_platform=$PROD_PLATFORM


    [testlink-maps]
    <testlink_internal_tc_id>=<test_file>::<test_class>::()::<testcase_method>


### pytest.ini configuration
    testlink_ini_file=testlink.ini
