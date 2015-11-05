oimp = {}
oimp.TOP_PAGE = "top"
oimp.start_time = util.time()
oimp.started = {}
oimp.tot_requests = 0
oimp.last_request = nil
oimp.scenario_name = nil -- to be set by oimp.top
oimp.top_pass_val = 1
-- oimp.top_pass_val can be set to 0 to indicate failure, but normally failure is done by:
--
-- oimp.done(0)
-- return
--

function oimp.should_log()
  return client.get_id() == 1
end

function oimp.debug(msg)
  if not oimp.should_log() then
    return
  end

  if not oimp_config.LOG_DEBUG then
    return
  end

  log.debug('DEBUG', msg)
end

function oimp.info(msg)
  if not oimp.should_log() then
    return
  end

  if not oimp_config.LOG_INFO then
    return
  end

  log.info('INFO', msg)
end

function oimp.error(msg)
  oimp.top_pass(0)
  if not oimp.should_log() then
    return
  end

  if not oimp_config.LOG_ERROR then
    return
  end

  if oimp_config.ERRORS_AS_INFO then
    log.info('ERROR', msg)
  else
    log.error('ERROR', msg)
  end
end

-- we must only set pass metric once for each test, to get correct pass counts
oimp.top_pass_set_already = false

function oimp.top_pass(pass)
  if oimp.top_pass_set_already then -- we must only set pass metric once for each test, to get correct pass counts
    return
  end
  oimp.top_pass_set_already = true
  if oimp_config.PRINT_TOP_PASS then
    oimp.info("top_pass " .. pass)
  end
  oimp.metric('pass', pass)
  oimp.metric(oimp.scenario_name .. '.pass', pass)
end

function oimp.profile(uri, trace)
  local doit = math.random(1, oimp_config.PROFILE_EACH) == 1

  if doit then
    local timestamp = os.time()
    uri = uri .. '&_x=' .. (trace or 'loadimpact')
    oimp.debug('Profiling ' .. uri)
  end

  return uri
end

function oimp.metric(name, value)
  if not oimp.should_log() then
    return
  end

  result.custom_metric(oimp_config.METRICS_TAG .. "." .. name, value)
  if oimp_config.LOG_METRICS then
    log.info('METRIC', oimp_config.METRICS_TAG .. "." .. name, ':', value)
  end
end

function oimp.log_response_metrics(res)
--  oimp.metric('status_code',         res['status_code'])
--  oimp.metric('connect_time',        1000 * res['connect_time'])
--  oimp.metric('dns_lookup_time',     1000 * res['dns_lookup_time'])
--  oimp.metric('ssl_handshake_time',  1000 * res['ssl_handshake_time'])
--  oimp.metric('redirect_time',       1000 * res['redirect_time'])
--  oimp.metric('time_to_first_byte',  1000 * res['time_to_first_byte'])
--  oimp.metric('download_time',       1000 * res['download_time'])
end

-- Perform a positive test. It returns true if the value matches the correct one.
function oimp.pass(page, metric, value, correct)
  if value == correct then
    oimp.metric(page .. '.' .. metric .. '.pass', 1)
    return true
  else
    local url_str = ""
    if oimp.last_request.url then
      url_str = " Url: " .. oimp.last_request.url .. "."
    end
    oimp.error('Value ' .. metric .. ' failed for page ' .. page .. '. Got ' .. tostring(value) .. ' instead of ' .. tostring(correct) .. '.' .. url_str .. ". Email: " .. email .. ". Client_id: " .. client_id)
    oimp.metric(page .. '.' .. metric .. '.pass', 0)
    return
  end
end

-- Perform a negative test. It returns false if the value matches the failure one.
function oimp.fail(page, metric, value, failure)
  if not page then -- if _page nil then use default top_page
    page = oimp.TOP_PAGE
  end
  local _page = page .. '.' .. metric
  if value == failure then
    oimp.error('Value ' .. metric .. ' failed. Got ' .. tostring(value) .. '.')
    oimp.metric(_page .. '.pass', 0)
    return true
  else
    oimp.metric(_page .. '.pass', 1)
    return
  end
end

function oimp.check_status(page, res, expected)
  return oimp.pass(page, 'status_code', res['status_code'], expected)
end

function oimp.before(page)
  http.page_start(page)
  local started = util.time() - oimp.start_time
  oimp.started[page] = started
  -- oimp.metric('request.before',  1000 * started)
  -- oimp.metric(page .. '.before', 1000 * started)
end

function oimp.after(page, res)
  http.page_end(page)
  local started = oimp.started[page]
  local stopped = util.time() - oimp.start_time
  local duration    = stopped - started
  -- oimp.metric('request.after',  1000 * stopped)
  -- oimp.metric(page .. '.after', 1000 * stopped)
  oimp.metric('request.duration',   1000 * duration)
  oimp.metric(page .. '.duration',  1000 * duration)
  oimp.log_response_metrics(res)
  oimp.started[page] = nil
end

function oimp.request(page, request, is_core_action)
  local report_results = oimp.should_log()
  request['response_body_bytes'] = request['response_body_bytes'] or oimp_config.RESPONSE_SIZE
  request['report_results'] = report_results
  oimp.tot_requests = oimp.tot_requests + 1
  if is_core_action then
    oimp.before("core_action") -- Needed to calculate actions/s for the central part of each test, excluding setup requests
  end
  oimp.before(page)
  local res = http.request(request)
  oimp.after(page, res)
  if is_core_action then
    oimp.after("core_action")
  end
  oimp.last_request = res
  return res
end

function oimp.top(scenario)
  oimp.scenario_name = "scenario_" .. scenario -- store global var
  oimp.start(oimp.scenario_name)
  foo = oimp_config.METRICS_TAG .. "." .. oimp.scenario_name
  http.page_start(oimp_config.METRICS_TAG .. "." .. oimp.scenario_name)
end

-- This function is called once, from oimp.top() on script start
function oimp.start(page)
  oimp.before(oimp_config.METRICS_TAG)
  oimp.before(page)
end


function oimp.done(pass)
  oimp.metric('total_requests', oimp.tot_requests)
  local page = oimp.scenario_name
  local started = oimp.started[page]
  if started then
    local stopped = util.time() - oimp.start_time
    local duration    = stopped - started
    oimp.metric(page .. '.duration',  1000 * duration)
  else
    log.error('Started for page ' .. page .. ' was not found.')
  end

  http.page_end(oimp_config.METRICS_TAG .. "." .. page)
  http.page_end(page)
  http.page_end(oimp_config.METRICS_TAG)

  if pass ~= nil then
    oimp.top_pass(pass)
  end
end

function oimp.bottom(scenario)
  oimp.pass(oimp_config.METRICS_TAG, 'check', oimp.top_pass_val, 1)
  oimp.done(oimp.top_pass_val)
end
