pytest-testlink-adaptor
=======================


Allow to update test results in Testlink TMS.

Uses testlink.ini file with test case id and test node id as mapping:

### Testlink file format (testlink.ini)
    [testlink-conf]
    xmlrpc_url =http://[test link server]/testlink/lib/api/xmlrpc.php
    api_key = <api_key> (can be generated in Testlink->My Settings->API interface->Generate Key)
    project =<Project name in test link>
    test_plan =Prefix $ to pick from environment variable.
    build_name =Prefix $ to pick from environment variable.
    tester =<tester_name> (tester name in Testlink for automatic execution)
    exit_on_fail=optional [False by default]

    new_build=optional [False by default] (with True will create a new build)

    [testlink-maps]
    <testlink_internal_tc_id>=<test_file>::<test_class>::()::<testcase_method>



### pytest.ini configuration
    testlink_ini_file=testlink.ini
