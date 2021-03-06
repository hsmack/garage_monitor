require 'sinatra'
require 'sqlite3'
require 'date'
require 'json'
require 'yaml'

set :environment, :production
set :port, 80


webapp_path = File.expand_path(File.dirname(__FILE__))

# load app config
APP_CONFIG = YAML.load_file("#{webapp_path}/../config/app_config.yml")
$db_file_path = "#{webapp_path}/../database/#{APP_CONFIG['database']['filename']}"


$db = SQLite3::Database.new($db_file_path)
$db.busy_timeout=APP_CONFIG['database']['timeout']

get '/' do
  @house_name = "My House"
  @door = $db.get_first_row("select * from door order by timestamp desc")
  @last50 = $db.execute("select * from door order by timestamp desc limit 50")
  time = DateTime.parse("#{@door[1]} -800").to_time
  if (Time.now - time) <= 24*60*60
    @time_str = "Today #{time.strftime('%b %d, %T')}"
  elsif ((Time.now - time) > 24*60*60) && ((Time.now - time) < 24*60*60*2)
    @time_str = "Yesterday #{time.strftime('%b %d, %T')}"
  else
    @time_str = time.strftime('%b %d, %T')
  end
  
  erb :index
end

get '/current.json' do
  content_type :json
  @door = $db.get_first_row("select * from door order by timestamp desc")
  @door.to_json
end

get '/last5.json' do
  content_type :json
  @last5 = $db.execute("select * from door order by timestamp desc limit 5")
  @last5.to_json
end

get '/last50.json' do
  content_type :json
  @last50 = $db.execute("select * from door order by timestamp desc limit 50")
  @last50.to_json
end

__END__
@@layout
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
  </head>
  <title>Garage Monitor</title>
  <link rel="stylesheet" href="http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css" />
  <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
  <script src="http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js"></script>
  <style typeg="text/css" media="screen">
    .center-wrapper{
      text-align: center;
    }
    .center-wrapper * {
      margin: 0 auto;
    }
    #house-image {
      margin-bottom: 10px;
    }
    #history-wrapper p {
      margin-top: 4px;
    }
  </style>
  <body>
  <%= yield %>
  </body>
</html>

@@ index
<!-- Home -->
<div data-role="page" id="page1">
    <div data-theme="a" data-role="header">
        <h3>
            <%= @house_name %>
        </h3>
    </div>
    <div data-role="content">
      <div class="center-wrapper">
        
        <div id="house-image">
          <% if @door[3] =~ /open/i %>
            <img src="alert-red-icon.png" width="150" height="150" alt="red alert, open garage is a problem" />
          <% else %>
            <img src="house-blue.png" width="150" height="150" alt="safe, garage is closed" />
          <% end %>
        </div>
        
        <div id="current-state">
          <b><%= @door[3].upcase %></b><br/><%= @time_str %>
        </div>
      
        <div id="history-wrapper" style="margin: 20px">
          <div class="history-title" style="text-align:left">
            <b>History</b>
          </div>            
          <div class="history-data"  style="text-align:left">
          <% @last50.each do |row| %>
            <% time = DateTime.parse("#{row[1]} -800").to_time %>
            <p><%= "#{time.strftime('%b %d, %T')}, #{row[3]}" %></p>
          <% end %>
          </div>
        </div>
      </div>
    </div>
</div>


