import os

from osgtest.library import core

def wait_for_daemon(collector_log_path, stat, daemon, timeout):
    """Wait until the requested 'daemon' is available and accepting commands by
    monitoring the specified CollectorLog from the position specified by 'stat'
    for a maximum of 'timeout' seconds. Returns True if the daemon becomes
    available within the timeout period and False, otherwise.

    """
    sentinel = r'%sAd\s+:\s+Inserting' % daemon.capitalize()
    return bool(core.monitor_file(collector_log_path, stat, sentinel, timeout)[0])

def config_val(attr):
    """Query HTCondor for the value of a configuration variable using the python
    bindings if available, condor_config_val otherwise

    """
    try:
        import htcondor2 as htcondor
        # Necessary for checking config between different flavors of HTCondor
        htcondor.reload_config()
        try:
            val = htcondor.param[attr]
        except KeyError: # attr is undefined
            val = None
    except:
        out, _, _ = core.check_system(('condor_config_val', attr),
                                      'Failed to query for config variable: %s' % attr)
        val = out.strip()
    return val

def ce_config_val(attr):
    """Query HTCondor-CE for the value of a configuration variable using the
    python bindings if available, condor_config_val otherwise

    """
    os.environ.setdefault('CONDOR_CONFIG', '/etc/condor-ce/condor_config')
    val = config_val(attr)
    del os.environ['CONDOR_CONFIG']
    return val
