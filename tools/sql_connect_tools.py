import pymysql
# from GaoXiaoYiKe import settings


class SQLConnectTools(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd='123456',
            db='test_flask4',
            charset='utf8',
        )
        self.cursor = self.connect.cursor()
    def get_user_id(self):
        sql_string = '''
            select id from user order by RAND() limit 1
        '''
        x = self.cursor.execute(sql_string)
        result = self.cursor.fetchone()[0]
        print(result)
        self.connect.commit()
        return result

    def get_image_id(self):
        sql_string = '''
            select id from image order by RAND() limit 1
        '''
        x = self.cursor.execute(sql_string)
        result = self.cursor.fetchone()[0]
        print(result)
        self.connect.commit()
        return result

    def get_image_url(self):
        sql_string = '''
            select url from image
        '''
        x = self.cursor.execute(sql_string)
        result = self.cursor.fetchall()
        self.connect.commit()
        return result

    def get_user_head_url(self):
        sql_string = '''
        select head_url from user
        '''
        x = self.cursor.execute(sql_string)
        result = self.cursor.fetchall()
        self.connect.commit()
        return result


    def get_username(self):
        sql_string = '''
        select username from user
        '''
        x = self.cursor.execute(sql_string)
        result = self.cursor.fetchall()
        self.connect.commit()
        return result

    def get_follows(self,user_id):
        sql = '''
        SELECT followed_id
        FROM followers
        WHERE follower_id={}
        '''.format(user_id)
        self.cursor.execute(sql)
        followed_ids = []
        results = self.cursor.fetchall()
        for result in results:
            # print(result[0])
            followed_ids.append(result[0])
        self.connect.commit()
        return followed_ids




if __name__ == '__main__':
    sql_tools = SQLConnectTools()
    ids = sql_tools.get_follows(110)
    print(ids)