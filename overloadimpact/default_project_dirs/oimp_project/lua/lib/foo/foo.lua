foo = {}
foo.some_var = "bar"

function foo.some_request(foo_param)
  local page = "foo_index"
  local users_ds  = datastore.open('users-DS_VERSION') -- get a versioned users DS
  user = users_ds:get_random()
  return oimp.request(page, {
                        'GET',
                        "http://www.examplefoo.com/index.html?user_email=" .. url.escape(user[1]) .. "&foo=" .. url.escape(foo_param)
  })
end
