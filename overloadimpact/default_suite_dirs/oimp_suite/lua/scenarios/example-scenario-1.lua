--- import common

local foo_res = foo.foo_request("bar")
if oimp.fail(page, 'foo_request', foo_res, nil) then
  oimp.done(0)
  return
end
