options = {}

function options.table_copy(obj, seen)
  if type(obj) ~= 'table' then return obj end
  if seen and seen[obj] then return seen[obj] end
  local s = seen or {}
  local res = setmetatable({}, getmetatable(obj))
  s[obj] = res
  for k, v in pairs(obj) do res[options.table_copy(k, s)] = options.table_copy(v, s) end
  return res
end

function options.overwrite_vals(tbl, overrides)
  -- Combine default with custom params
  for key,val in pairs(overrides) do
    if type(val) == 'table' then
      tbl[key] = options.overwrite_vals(tbl[key], val)
    else
      if val == "NIL" then -- unset default value
        tbl[key] = nil
      else
        tbl[key] = val
      end
    end
  end
  return tbl
end

function options.overwrite_defaults(defaults, overrides)
    -- Default params
  local new_options = options.table_copy(defaults)
  return options.overwrite_vals(new_options, overrides)
end