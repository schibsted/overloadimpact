cookies = {}

cookies.global_cookies = nil
cookies.MANUAL_HANDLING = false

cookies.capture_keys = {}

function cookies.add_capture_key(key)
  table.insert(cookies.capture_keys, key)
end

function cookies.init(response)
  cookies.global_cookies = response.cookies
end

-- Must be called in the beginning of test, because the http option auto_cookie_handling can only be set once
function cookies.enable_manual_cookies(enable)
  cookies.MANUAL_HANDLING = enable
  http.set_option("auto_cookie_handling", not enable)
end

function cookies.encode(cookies)
  str = ""
  for key,value in pairs(cookies) do --pseudocode
    str = str .. key .. "=" .. value .. ";"
  end
  return str
end

function cookies.set(key, val)
  cookies.global_cookies[key] = val
end

function cookies.update(res)
  for i, key in ipairs(cookies.capture_keys) do
    -- Overwrite session cookie with new value after login
    if res.cookies[key] then
      cookies.global_cookies[key] = res.cookies[key]
    end
  end
end

function cookies.capture_redirect(page, start_res, capture_key, destination_regex)
  if cookies.MANUAL_HANDLING then
    local status_code = start_res.status_code
    local next_location = start_res.headers['Location'][1]
    oimp.debug("cookie_cap first next_location:" .. next_location)
    local counter = 0

    current_res = start_res

    while status_code == 302 and not string.match(next_location, destination_regex)
    do
      counter = counter + 1
      local page_redirect = page .. '.count.' .. counter
      next_url = oimp_config.TARGET_SERVER
      next_url = next_url .. next_location
      next_url = oimp.profile(next_url, page_login)

      current_res = oimp.request(page_redirect, {
                                      'GET',
                                      next_url,
                                      auto_redirect = false,
                                      headers={["Cookie"]=cookies.encode(cookies.global_cookies)}
      })

      status_code = current_res.status_code
      if status_code == 302 then
        next_location = current_res.headers['Location'][1]
      else
        -- url = current_res.url
        -- oimp.info("url:" .. url)
      end
    end

    if capture_key and current_res.cookies[capture_key] then
      cookies.global_cookies[capture_key] = current_res.cookies[capture_key]
    end
  end
  return {["response"] = current_res, ["location"] = next_location}
end

function cookies.cookie_headers()
  if cookies.global_cookies then
    oimp.debug("headers global_cookies:" .. json.stringify(cookies.global_cookies))
  else
    oimp.debug("headers global_cookies: nil")
  end
  if cookies.MANUAL_HANDLING then
    headers = {}
    headers["Cookie"] = cookies.encode(cookies.global_cookies)
  else
    headers = nil
  end
  return headers
end


function cookies.get_global()
  return cookies.global_cookies
end

function cookies.manual_handling_enabled()
  return cookies.MANUAL_HANDLING
end

function cookies.encoded_global()
  return cookies.encode(cookies.get_global())
end