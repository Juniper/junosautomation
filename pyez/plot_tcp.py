import time
from bokeh.plotting import figure, output_server, cursession, show
from bokeh.models import NumeralTickFormatter

from jnpr.junos import Device

# prepare output to server
output_server("animated_line")

p = figure(plot_width=600, plot_height=600)
dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False, port=22)
dev.open()

x_tmp = [0]*5
x_var = [0]*5
ct = time.localtime()
ct = ct.tm_hour*3600+ct.tm_min*60+ct.tm_sec
op = dev.rpc.get_statistics_information(tcp=True)
packets_sent_new = op.xpath('.//packets-sent')[0].text.strip()
packets_recv_new = op.xpath('.//packets-received')[0].text.strip()
p.line([ct, ct+2, ct+4, ct+6, ct+8], x_tmp, name='ex_line',  legend = 'packets-sent')
p.line([ct, ct+2, ct+4, ct+6, ct+8], x_var, name='ex_line', line_color="red", legend = 'packets-recv')
p.xaxis[0].formatter = NumeralTickFormatter(format='00:00:00')
show(p)

# create some simple animation..
# first get our figure example data source
renderer = p.select(dict(name="ex_line"))
ds1 = renderer[0].data_source
ds2 = renderer[1].data_source
while True:
    op = dev.rpc.get_statistics_information(tcp=True)
    packets_sent_new, packets_sent_old = op.xpath('.//packets-sent')[0].text.strip(), packets_sent_new
    packets_recv_new, packets_recv_old = op.xpath('.//packets-received')[0].text.strip(), packets_recv_new
    ct = time.localtime()
    ct = ct.tm_hour*3600+ct.tm_min*60+ct.tm_sec
    ds2.data["x"] = ds1.data["x"] = [ct, ct+2, ct+4, ct+6, ct+8]
    ds1.data["y"] = ds1.data["y"][1:]+[int(packets_sent_new)-int(packets_sent_old)]
    ds2.data["y"] = ds2.data["y"][1:]+[int(packets_recv_new)-int(packets_recv_old)]
    cursession().store_objects(ds1, ds2)
    time.sleep(1.5)
