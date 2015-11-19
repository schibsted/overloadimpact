foo = {}
foo.some_var = "bar"

function foo.some_request(foo_param)
  local page = "foo_index"
  local users_ds  = datastore.open('users-DS_VERSION') -- get a versioned users DS
  local user = users_ds:get_random()
  local url = "http://www.examplefoo.com/index.html?user_email=" .. url.escape(user[1]) .. "&foo=" .. url.escape(foo_param)
  return oimp.request(page,
                      {
                        'GET',
                        url,
                      },
                      true -- is_core_action = true, signals that this the core action of this scenario
  )
end
