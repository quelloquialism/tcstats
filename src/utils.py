def make_row(row, format):
  print "ROW:::", row
  print "FORMAT:::", format
  return "<tr><td>" + \
      "</td><td>".join(format[i] % row[i] for i in range(len(row))) + \
      "</td></tr>"

def make_table(data, titles=None, format=None):
  if len(data) > 0:
    table_width = len(data[0])
  else:
    return ""
  prefix = "<table>"
  suffix = "</table>"
  if format is None:
    format = ["%s"] * table_width
  print "DATA:::", data
  table_body = "".join(make_row(r, format) for r in data)
  if titles is not None:
    table_body = make_row(titles, ["%s"] * table_width) + table_body
  return prefix + table_body + suffix

