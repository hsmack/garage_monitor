require "sinatra"
require "pi_piper"
require 'pp'

$leds = {"18" => 'red', "15" => "yellow", "14" => "green"}
$pins =[]
$leds.each do |pin, color|
  pin = pin.to_i
  $pins[pin] =  PiPiper::Pin.new(pin: pin, direction: :out)
end

def read_led(pin)
  $pins[pin].read
end

def write_led(pin, value)
  puts "pin: #{pin} -> #{value}"
  $pins[pin].update_value value
end

get '/' do
  erb :index
end

get '/write' do
  led_status = params[:led]
  if led_status && !led_status.empty?
    led_status.each do |pin, value|
      write_led(pin.to_i, value.to_i)
    end
  end
  ""
end

__END__
@@layout
<html>
  <body>
  <%= yield %>
  </body>
</html>

@@ index
<style type="text/css" media="screen">
  body { padding: 0; margin: 0; }
  table { border-spacing: 0; border-collapse: 0;}
  td { opacity:0.4; filter:alpha(opacity=40); }
  td.red { background-color: red; }
  td.yellow { background-color: yellow; }
  td.green { background-color: green; }
  .active { opacity: 1; filter:alpha(opacity=100); }
</style>

<table width="100%" height="100%" border="0">
  <% $leds.each do |pin, color|%>
  <% active = read_led(pin.to_i) %>
  <tr>
    <td class="<%= color %> <%= "active" if active == 1 %>" data-pin="<%= pin %>" data-active="<%= active %>"></td>
  </tr>
  <% end %>
</table>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>
<script type="text/javascript" charset="utf-8">
  $(function(){
    $("td").click(function(e){
      var el = $(this),
      active = el.data('active'),
      pin = el.data('pin'),
      data ={};

      active = active == 0 ? 1 : 0;
      data[pin] = active;

      $.get('/write', {"led": data}, function(){
        if (active == 1) {
          el.addClass('active');
        } else {
          el.removeClass('active');
        }
        el.data('active', active);
      });
    });
  })
</script>
