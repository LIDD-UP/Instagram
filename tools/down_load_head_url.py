import requests
from tools.sql_connect_tools import SQLConnectTools
import re


if __name__ == '__main__':
    sql_tools = SQLConnectTools()
    results = sql_tools.get_user_head_url()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/63.0.3239.132 Safari/537.36'}
    for index,result in enumerate(results):
        print(result)
        try:
            image = requests.get(url=str(result[0]),headers=header)
            if re.findall(r'\.jpg',result[0]):
                print(image.content)
                with open('./head_urls_images/{}.jpg'.format(index), 'wb') as f:
                    f.write(image.content)
            else:
                with open('./head_urls_images/{}.png'.format(index), 'wb') as f:
                    f.write(image.content)
        except Exception:
            print(Exception)
        # continue






