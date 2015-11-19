
inspect = {}

function inspect.inspect(key, val, indent)
  -- if LOG_DEBUG == false then return end
  indent = indent or 0
  local pad = string.rep("--", indent)
  logger.debug(pad .. "--> ", key, "(" .. type(val) .. ")", val)

  if type(val) == "table" then
    for k, v in pairs(val) do
      oimp.inspect(k, v, indent + 1)
    end
  end
end

function inspect.response(res)
  local fields = {
    'body',
    'body_size',
    'compressed',
    'compressed_body_size',
    'connect_time',
    'content_type',
    'cookies',
    'dns_lookup_time',
    'download_time',
    'header_size',
    'headers',
    'ip',
    'redirect_time',
    'request_method',
    'request_size',
    'request_url',
    'ssl_handshake_time',
    'status_code',
    'status_msg',
    'time_to_first_byte',
    'total_load_time',
    'url',
  }

  for k, v in pairs(fields) do
    inspect.inspect(v, res[v])
  end
end
