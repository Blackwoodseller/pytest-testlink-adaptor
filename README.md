# pytest-testlink-adaptor

Allow to update test results in Testlink TMS.

Uses testlink.ini file with test case id and test node id as mapping:
Every parameter value can be hardcoded or defined via environment variable
(e.g. test_plan=$TESTPLAN). For more detail, please see testlink.ini.expample

## Testlink file format (testlink.ini)
### [testlink-conf]

* ``xmlrpc_url=http://[test link server]/testlink/lib/api/xmlrpc.php`` Specify Endpoint for testpink API
* ``api_key=<api_key>`` Secret key, can be generated in Testlink->My Settings->API interface->Generate Key)
* ``tester=<tester_name>`` Tester name in Testlink for automatic execution
* ``project=<Project name in TestLink>``
* ``test_plan=<test_plan_name>`` Test plan in TestLink for specified project 
* ``testlink_tc_prefix=TC-`` Prefix for testcases in TestLink project
* ``build_name=<build_name>`` Build name will be create in TestLink if it does not exist
* ``prod_platform=<product_platform>`` Product test platform in the Testlink test plan
* ``test_plan=<test_plan_name>`` Test plan in TestLink for specified project
 
### [testlink-maps]

Simple test:
* ``<testlink_testcase>=<pytest_method>``

Test with parametrization:
* ``<testlink_testcase>=<pytest_method>[<parameter_name>]``


## pytest.ini configuration

``testlink_ini_file=testlink.ini``
    
## Parameters

``--no-testlink`` disable pluggin, test results won't be saved in TestLink

``--testlink-exit-on-error`` exit on any test link plugin related errors/exceptions
