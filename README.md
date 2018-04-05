In the userdata of your instance have something like the below

```json
{"ssm":{"prefix":"/coolapp/dev/","destination":"/etc/environment"}}
```

In the instance AMI have python installed and config it to run ssm-parameters-env.py as root or admin

On Linux before run this prior to starting the app

```bash
#set env variables
set -o allexport
source /etc/environment
set +o allexport
```

On Windows start your app (or run issreset) after running ssm-parameters-env.py

### Supported types

 - ps1/ - SSW parameter value is executed as powershell
 - cmds/ - cmds are executed in bash on Linux
 - files/ - The value of the SSM parameter is saved to the key path
 - env/ - Set an env variable with the name of the SSM parameter key

### Current limitations
 - On bash $ signs need to be escaped due to how soure works to load the variables

