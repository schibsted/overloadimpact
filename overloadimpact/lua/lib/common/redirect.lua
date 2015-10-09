redirect = {}

-- Prepares a redirect url, adding domain (target_server) if missing
function redirect.prepare_url(page, location)
  local uri = nil
  local parsed = url.parse(location)
  if parsed.host then
    uri = location
    oimp.info('Using full URL: ' .. uri)
  else
    uri = oimp_config.TARGET_SERVER
    uri = uri .. location
    uri = oimp.profile(uri, page)
  end
  return uri
end

function redirect.request(page, location, auto_redirect)
  if oimp.fail(page, 'redirect_request.location', location) then
    return
  end

  res = oimp.request(page, {
                        'GET',
                        redirect.prepare_url(page, location),
                        headers = cookies.cookie_headers(),
                        auto_redirect = auto_redirect,
  })
  return res
end
