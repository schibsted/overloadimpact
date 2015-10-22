import numpy
import datetime
import pygal
from pygal.style import CleanStyle

def pygal_line():
    # For custom styling see http://pygal.readthedocs.org/en/latest/documentation/custom_styles.html
    chart = pygal.Line(fill=False, style=CleanStyle, show_minor_x_labels=False, x_labels_major_count=10, x_label_rotation=90, width=1000, height=500)
    return chart

def pygal_bar():
    # For custom styling see http://pygal.readthedocs.org/en/latest/documentation/custom_styles.html
    chart = pygal.Bar(fill=False, style=CleanStyle, show_minor_x_labels=False, x_labels_major_count=10, x_label_rotation=90, width=1000, height=800, truncate_label=100)
    return chart

def get_start_time(metrics):
    timestamp = metrics["__li_live_feedback"][0]["timestamp"]
    return datetime.datetime.fromtimestamp(__to_secs(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

def make_time_chart(report_path, metrics, title, chart_name, run_id, y_label, rows, y_key, dest_dir, display_active_clients, active_clients):
    chart = pygal_line()
    chart.title = title

    # get the time labels for the x_axis
    timestamps = map(lambda row: row["timestamp"], rows)
    time_labels = make_time_labels(timestamps)
    chart.x_labels = time_labels

    # display requested main metric
    y_vals = map(lambda row: row[y_key], rows)
    chart.add(y_label, y_vals)

    # display active clients metric
    if display_active_clients:
        if y_vals[-1] == 1 and y_vals[0] == 1:
            y_vals[-1] = y_vals[-1] - 0.000001 # work around to avoid render errors when all y_vals are exactly 1
        chart.add('Active clients', active_clients, secondary=True)

    chart.render_to_file(report_path + "/" + dest_dir + "/" + chart_name + ".svg")

def make_time_labels(timestamps):
    time_labels = map(lambda timestamp: datetime.datetime.fromtimestamp(__to_secs(timestamp)).strftime("%H:%M:%S"), timestamps)
    return time_labels

def __to_secs(num):
    to_sec_divisor = 1000000
    return int(num) / to_sec_divisor

def chart_markup(chart, x_axis_label="Time"):
    return """<figure>
      <embed width="1100px" id=\"""" + chart + """_svg" type="image/svg+xml" src=\"""" + chart + """.svg" />
      <figcaption style="text-align: center;">""" + x_axis_label + """</figcaption>
    </figure>
      <br/>
"""

def get_last_timestamp(metrics):
    return metrics["__li_live_feedback"][-1]["timestamp"]

def header(title, subtitle, subtitle2):
    markup = """<!DOCTYPE html>
<html>
  <head>
    <!-- ... -->
  </head>
  <body>
    <h1>""" + title + """</h1>
    <h2 style="font-weight: lighter">""" + subtitle + """</h2>
    <h2 style="font-weight: lighter">""" + subtitle2 + """</h2>
"""
    return markup

def footer():
    markup = """</body>
</html>"""
    return markup

def section_title(title, comment):
    return """</div>
    <h2 style="font-weight: lighter">""" + title + """</h2><span style="font-style: italic">""" + comment + """</span><br/>
"""

def link_title(file_path, title, sub_title):
    return """<div class="link_title"><h3><a href="%s">%s</a></h3><span class="link_subtitle" style="font-style: italic">%s</span></div>""" % ("file://" + file_path, title, sub_title)

def section(title, markup):
    return """<div class="section"><h2>%s</h2>%s</div>""" % (title, markup)

def paragraph(markup):
    return """<p class="paragraph">%s</p>""" % (markup)

def arr_avg(arr, key):
    vals = map(lambda row: row[key], arr)
    return numpy.mean(vals)
