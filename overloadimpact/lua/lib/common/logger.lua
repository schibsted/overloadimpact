
function dbg(msg)
  if oimp_config.DO_DEBUG then
    log.debug(msg)
  end
end

function err(msg)
  if oimp_config.DO_ERR then
    log.error(msg)
  end
end
