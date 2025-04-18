# ok.ru-and-vk.ru-to-m3u

## Notes
Only tested on Windows <br>
See troubleshooting if you have issues launching mitmproxy due to dependencies

## Requirements
python - must be 3.10 or higher (3.8 or lower is not supported by streamlink) <br>
install [streamlink](https://streamlink.github.io/install.html) and make it available at path <br>
flask (can be installed by typing ```pip install flask``` at cmd/terminal window) <br>
mitmproxy (can be installed by typing ```pip install mitmproxy``` at cmd/terminal window)

## Verify streamlink install
To test streamlink install type in a new cmd/terminal window
```
streamlink --version
```
The output should be
streamlink "version number" eg 7.1.1 <br>
If it says unknown command/'streamlink' is not recognized as an internal or external command,
operable program or batch file. <br>
Then you need to make sure you have installed streamlink to path/environmental variables

## How To Use (without threadfin)
This version uses its own buffer and redirect which aids in stream stability however it may not work on all systems. If you have issues changing channels eg all channels are the same etc use the with threadfin version <br>
<br>
Open main.py with a code text editor <br>
Change the IP address in the line starting ```command1 =``` to the IP of the machine running the script <br>
<br>
Open stream_link_server.py with a code text editor <br>
Change the IP address in the lines starting ```proxy_url =``` and ```return redirect``` to the IP address of the machine running the script <br>

Note you can change port numbers but if you change the proxy port or the flask port you need to also change the corresponding proxy port in the main.py file and the flask port in the m3u file

## How To Use (with threadfin)
This is the same as without threadfin with the following additions <br>
Change <br>
```
command2 = "python stream_link_server.py"
```
To <br>
```
command2 = "python stream_link_server_threadfin.py"
```

Note if your aim is to access the streams outside of your network (different to what the streamlink server is running on) you will have to replace all the IP address with public IPs and port forward ports on your router/firewall - I will not be providing support for this!

## Create an m3u file
Create an m3u file for the streams you want to play <br>
You need to prefix each url with ```http://192.168.1.123:7085/stream?url=``` changing the IP to the IP address of the machine running the script (the port is the flask port from stream_link_server.py) <br>
<br>
Here is an example

```
#EXTM3U
#EXTINF:-1 tvg-name="TMFRU" tvg-id="Music.Dummy.us" tvg-logo="https://tv2free.ru/sites/default/files/styles/large/public/tv-logo/tv-tmf-rus.jpg?itok=KyF1zaM5" group-title="Music",TMF RU
http://192.168.1.123:7085/stream?url=https://ok.ru/live/6195706404393
#EXTINF:-1 tvg-name="EuroDance90" tvg-id="Music.Dummy.us" tvg-logo="https://tv2free.ru/sites/default/files/styles/large/public/tv-logo/tv-eurodance-90-hd.jpg?itok=Nr_oAx6e" group-title="Music",EURODANCE 90
http://192.168.1.123:7085/stream?url=https://vk.ru/video-223902219_456239404
```

## How To Run - Windows and some linux
python main.py on windows 11 or python3 main.py on linux
<br>
Open the m3u file <br>
Script must be running for the m3u to work

## How To Run - Linux and others
Run manually <br>
<br>
In one terminal window run
```
mitmproxy -s mitmproxyserver.py --listen-host 192.168.1.123 --listen-port 7086
```

Change IP in above command to IP of machine running the script <br>
<br>
Then in another terminal window run <br>
python3 stream_link_server.py or python3 stream_link_server_threadfin.py

## Troubleshooting
If mitmproxy moans about moduels not being installed or errors on launch it's probably due to module versions not being correct. Try doing the following from the location of where the scripts are <br>

```
python3 -m venv myenv
source myenv/bin/activate
pip install mitmproxy==11.0 blinker==1.9.0 flask==3.0.3 werkzeug==3.0.3 jinja2==3.1.4 markupsafe==2.1.5 click==8.1.7 pyOpenSSL==24.3.0 cryptography==42.0.8 urllib3==2.2.3 certifi==2024.12.14 h2==4.1.0 wsproto==1.2.0 pyparsing==3.2.1 mitmproxy-rs==0.9.3 asgiref==3.8.1 msgpack==1.0.8 protobuf==5.27.2 publicsuffix2==2.20191221 pyperclip==1.8.2 sortedcontainers==2.4.0 zstandard==0.23.0
```

Then run mitmproxy again
