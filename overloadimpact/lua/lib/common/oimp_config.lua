-- Use this file to set global variables
oimp_config = {}

oimp_config.DO_DEBUG = false
oimp_config.DO_ERR = true

oimp_config.METRICS_TAG = 'app.'
oimp_config.PROFILE_EACH = 1000
oimp_config.RESPONSE_SIZE = 123456789

oimp_config.LOG_METRICS         = false
oimp_config.LOG_DEBUG           = false
oimp_config.LOG_INFO            = true
oimp_config.LOG_ERROR           = true

-- LoadImpact sometimes kills test when to many errors are printed, printers errors as info could possibly fix the problem
oimp_config.ERRORS_AS_INFO = false
oimp_config.PRINT_TOP_PASS = false
