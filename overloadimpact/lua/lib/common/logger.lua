logger = {}

function logger.should_log()
  return client.get_id() == 1
end

function logger.debug(msg)
  if not logger.should_log() then
    return
  end

  if not oimp_config.LOG_DEBUG then
    return
  end

  log.debug('DEBUG', msg)
end

function logger.info(msg)
  if not logger.should_log() then
    return
  end

  if not oimp_config.LOG_INFO then
    return
  end

  log.info('INFO', msg)
end

function logger.error(msg)
  log.error('ERROR', msg)
end

function dbg(msg)
  if oimp_config.DO_DEBUG then
    logger.debug(msg)
  end
end

function err(msg)
  if oimp_config.DO_ERR then
    logger.error(msg)
  end
end
