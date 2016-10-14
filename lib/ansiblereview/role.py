from ansiblereview import Result, Error
import codecs
import yaml


# candidate for ansiblereview.roles
def metamain_check(candidate, settings, fn):
    try:
        fh = codecs.open(candidate.path, mode='rb', encoding='utf-8')
    except IOError, e:
        result = Result(candidate)
        result.errors = [Error(None, "Could not open %s: %s" %
                               (candidate.path, e))]
    try:
        result = Result(candidate)
        data = yaml.safe_load(fh)
        result.errors = fn(data)
    except Exception, e:
        result.errors = [Error(None, "Could not parse in %s: %s" %
                               (candidate.path, e))]
    finally:
        fh.close()
    return result
