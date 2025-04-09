# okru-to-m3u

## Notes
Only tested on Windows

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

## How To Use
Open main.py with a code text editor <br>
Change the IP address in the line starting ```command1 =``` to the IP of the machine running the script <br>
<br>
Open stream_link_server.py with a code text editor <br>
Change the IP address in the lines starting ```proxy_url =``` and ```return redirect``` to the IP address of the machine running the script <br>

Note you can change port numbers but if you change the proxy port or the flask port you need to also change the corresponding proxy port in the main.py file and the flask port in the m3u file

## Create an m3u file
Create an m3u file for the streams you want to play <br>
You need to prefix each url with ```http://192.168.1.123:7085/stream?url=``` changing the IP to the IP address of the machine running the script (the port is the flask port from stream_link_server.py) <br>
<br>
Here is an example

```
#EXTM3U
#EXTINF:-1 tvg-name="TMFRU" tvg-id="Music.Dummy.us" tvg-logo="https://tv2free.ru/sites/default/files/styles/large/public/tv-logo/tv-tmf-rus.jpg?itok=KyF1zaM5" group-title="Music",TMF RU
http://192.168.1.123:7085/stream?url=https://ok.ru/live/6195706404393
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
python3 stream_link_server.py

## Troubleshooting
If mitmproxy moans about moduels not being installed or errors on launch it's probably due to module versions not being correct. Try doing the following from the location of where the scripts are <br>

```
python3 -m venv myenv
source myenv/bin/activate
pip install mitmproxy==11.0 blinker==1.6.2 flask==2.1.3 werkzeug==2.3.8 jinja2==3.1.2 markupsafe==2.1.5 click==8.1.7 pyOpenSSL==23.2.0 cryptography==41.0.2 urllib3==1.26.18 certifi==2024.2.2 h2==4.1.0 wsproto==1.2.0 pyparsing==3.0.9 mitmproxy-rs==0.6.2 asgiref==3.7.2 msgpack==1.0.0 protobuf==4.24.0 publicsuffix2==2.20190812 pyperclip==1.8.2 sortedcontainers==2.4.0 zstandard==0.18.0
```

Then run mitmproxy again
