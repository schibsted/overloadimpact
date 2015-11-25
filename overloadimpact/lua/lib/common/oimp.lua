oimp = {}
oimp.start_time = util.time() -- used for scenario timing

---------------------------------------------------------------------------------------------
-- Profiling functions

function oimp.profile(uri, trace)
  local doit = math.random(1, oimp_config.PROFILE_EACH) == 1

  if doit then
    local timestamp = os.time()
    uri = uri .. '&_x=' .. (trace or 'loadimpact')
    logger.debug('Profiling ' .. uri)
  end

  return uri
end

---------------------------------------------------------------------------------------------
-- Metric functions

-- Report a metric value to loadimpact.
function oimp.metric(name, value)
  if not logger.should_log() then
    return
  end

  result.custom_metric(oimp_config.METRICS_TAG .. "." .. name, value)
  if oimp_config.LOG_METRICS then
    log.info('METRIC', oimp_config.METRICS_TAG .. "." .. name, ':', value)
  end
end

-- Log response times as metrics, currently disabled
function oimp.log_response_metrics(res)
--  oimp.metric('status_code',         res['status_code'])
--  oimp.metric('connect_time',        1000 * res['connect_time'])
--  oimp.metric('dns_lookup_time',     1000 * res['dns_lookup_time'])
--  oimp.metric('ssl_handshake_time',  1000 * res['ssl_handshake_time'])
--  oimp.metric('redirect_time',       1000 * res['redirect_time'])
--  oimp.metric('time_to_first_byte',  1000 * res['time_to_first_byte'])
--  oimp.metric('download_time',       1000 * res['download_time'])
end

-- Called just before a scenario ends for metrics purposes
--
-- Finishes timing metrics and reports top_pass status (pass(1) or fail(0))
function oimp.done(pass)
  oimp.metric('total_requests', oimp.tot_requests)
  local page = oimp.scenario_name
  local started = oimp.started[page]
  if started then
    local stopped = util.time() - oimp.start_time
    local duration    = stopped - started
    oimp.metric(page .. '.duration',  1000 * duration)
  else
    logger.error('Started for page ' .. page .. ' was not found.')
  end

  http.page_end(oimp_config.METRICS_TAG .. "." .. page)
  http.page_end(page)
  http.page_end(oimp_config.METRICS_TAG)

  if pass ~= nil then
    oimp.__top_pass(pass)
  end
end


-- flag to ensure we only set pass metric once for each test, to get correct pass counts
oimp.top_pass_set_already = false

-- Private function to report a metric on whether this scenario as a whole failed or passed.
function oimp.__top_pass(pass)
  if oimp.top_pass_set_already then -- we must only set pass metric once for each test, to get correct pass counts
    return
  end
  oimp.top_pass_set_already = true
  if oimp_config.PRINT_TOP_PASS then
    logger.info("top_pass " .. pass)
  end
  oimp.metric('pass', pass)
  oimp.metric(oimp.scenario_name .. '.pass', pass)
end

---------------------------------------------------------------------------------------------
-- Result check functions

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

oimp.TOP_PAGE = "top" -- The prefix for top pages

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

-- Test if request result status_code matched the expected status_code
function oimp.check_status(page, res, expected)
  return oimp.pass(page, 'status_code', res['status_code'], expected)
end

-- Report and error and set scenario to failed (oimp.top_pass(0)).
function oimp.error(msg)
  oimp.__top_pass(0)
  if not logger.should_log() then
    return
  end

  if not oimp_config.LOG_ERROR then
    return
  end

  if oimp_config.ERRORS_AS_INFO then
    logger.info(msg)
  else
    logger.error(msg)
  end
end

---------------------------------------------------------------------------------------------
-- Timing functions

oimp.started = {}

-- Start timing for a given page
function oimp.before(page)
  http.page_start(page)
  local started = util.time() - oimp.start_time
  oimp.started[page] = started
end

-- End timing for a given page, and report metrics
function oimp.after(page, res)
  http.page_end(page)
  local started = oimp.started[page]
  local stopped = util.time() - oimp.start_time
  local duration    = stopped - started
  oimp.metric('request.duration',   1000 * duration)
  oimp.metric(page .. '.duration',  1000 * duration)
  oimp.log_response_metrics(res)
  oimp.started[page] = nil
end

---------------------------------------------------------------------------------------------
-- Request functions

oimp.tot_requests = 0
oimp.last_request = nil

-- Executes an http requests
--
-- Adds timing metrics for the request. The metrics are labelled with the page arg.
--
-- If core_action, then add core_action metrics.
function oimp.request(page, request, is_core_action)
  local report_results = logger.should_log()
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

---------------------------------------------------------------------------------------------
-- Script header and footer functions

oimp.scenario_name = nil -- to be set by oimp.top

-- Automatically added at the beginning of every scenario
function oimp.top(scenario)
  oimp.scenario_name = "scenario_" .. scenario -- store global var
  oimp.start(oimp.scenario_name)
  foo = oimp_config.METRICS_TAG .. "." .. oimp.scenario_name
  http.page_start(oimp_config.METRICS_TAG .. "." .. oimp.scenario_name)
end

oimp.top_pass_val = 1
-- oimp.top_pass_val can be set to 0 to indicate failure, but normally failure is done by:
--
-- oimp.done(0)
-- return
--

-- Automatically added at the bottom of every scenario
function oimp.bottom(scenario)
  oimp.pass(oimp_config.METRICS_TAG, 'check', oimp.top_pass_val, 1)
  oimp.done(oimp.top_pass_val)
end

-- This function is called once, from oimp.top() on script start
function oimp.start(page)
  oimp.before(oimp_config.METRICS_TAG)
  oimp.before(page)
end

---------------------------------------------------------------------------------------------
-- Deprecated logger functions

function oimp.debug(msg)
  logger.debug(msg)
end

function oimp.info(msg)
  logger.info(msg)
end