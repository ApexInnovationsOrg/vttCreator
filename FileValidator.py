import os
import re
import json
import requests
class FileValidator: 

    def __init__(self, params):
        self.url = params.get('url')
        self.hash = params.get('hash')
        self.regex = r'(?:\d+)\s(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\s+(.+?)(?:\n\n|$)'
        self.offset_seconds = lambda ts: sum(howmany * sec for howmany, sec in zip(map(int, ts.replace(',', ':').split(':')), [60 * 60, 60, 1, 1e-3]))

    def is_valid_url(self):
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return self.url is not None and regex.search(self.url)

    def has_valid_params(self):
        if not self.url:
            raise Exception("Url is required")
        if not self.hash:
            raise Exception("Hash is required")
        if not self.is_valid_url():
            raise Exception("The url informed is invalid.")

    def download_file(self):
        try:
            file = requests.get(self.url)
            with open("temp/" + self.hash + ".mp3", 'wb') as f:
                f.write(file.content) 
        except Exception as error:
            raise Exception("Can't download the file from this url.")
        self.fileDIR = "temp/" + self.hash + ".mp3"
        return self.fileDIR

    def sendError(self, error):
        webhook = "https://webhook.site/729bd33a-b191-402c-9598-13c1adb87a71"
        r = requests.get(url = webhook, params = {
            error: error
        })
        return True;

    def create_closed_caption(self):

        self.hash = "example-HASH1205425"
        self.fileDIR = "temp/" + self.hash + ".mp3"

        self.sendError("Variables Setup")
        if not os.path.isfile(self.fileDIR):
             self.sendError("The example file is not found.")
             return;
        try:
            # use autosrt to convert .mp3 to .srt
            command = 'echo "Terminal Executed" '
            command2 = 'autosrt --version'
            command3 = 'autosrt -S en -D en ' + '"' + self.fileDIR + '"'
            try:
                res = os.system(command)
                command2 = os.system(command2)
                command3 = os.system(command3)
                if res!= 0:
                    self.sendError("Command1 Failed")
                    return;
                if command2!= 0:
                    self.sendError("Command2 Failed")
                    return;
                if command3!= 0:
                    self.sendError("Command3 Failed, but it's expected to fail, so it's okay")
                    return;
            except Exception as error:
                self.sendError(error)
                self.sendError(json.dumps(error))
                return;
            # #delete old file
            self.sendError("AutoSRT was executed successfully.")
            if not os.path.isfile("temp/" + self.hash + ".srt"):
                self.sendError("The SRT file was not found.")
                return;
            # self.remove_file()
        except Exception as error:
            self.sendError(json.dumps(error))
            return;

    def format(self):
        self.srtDIR = 'temp/' + self.hash + '.srt'
        if not os.path.isfile(self.srtDIR):
            raise Exception("The SRT file is not found. - EXC3")
        try:
            # get content from srt and convert to json
            transcript = [dict(startTime = self.offset_seconds(startTime), endTime = self.offset_seconds(endTime), ref = ' '.join(ref.split())) for startTime, endTime, ref in re.findall(self.regex, open(self.srtDIR).read(), re.DOTALL)]
            #convert to json
            json_transcript = json.dumps(transcript, indent = 4)
            #delete .srt from temp
            os.remove(self.srtDIR)
            return json_transcript
        except Exception as error:
            raise Exception("Can't convert SRT to JSON - EXC4")

    def remove_file(self):
        try:
            os.remove(self.fileDIR)
        except Exception as error:
            raise Exception("Can't remove the file from the temp folder.")
        