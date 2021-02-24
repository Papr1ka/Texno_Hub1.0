from pymongo import MongoClient

class User():
    def __init__(self, id):
        self.user_id = id
        self.exp = 0
        self.money = 0
        self.voice = 0
        self.messages = 0
        self.custom_text = ""
        self.inventory = []
        self.custom_roles = []

    def raw(self):
        return {
            "user_id" : self.user_id,
            "exp" : self.exp,
            "money" : self.money,
            "voice" : self.voice,
            "messages" : self.messages,
            "custom_text" : self.custom_text,
            "inventory" : self.inventory,
            "custom_roles" : self.custom_roles
        }

class Voice_Channel():
    def __init__(self, channel_id, role_id, member_id, support_id):
        self.channel_id = channel_id
        self.role_id = role_id
        self.admin = member_id
        self.support_id = support_id
    
    def raw(self):
        return {
            "channel_id" : self.channel_id,
            "role_id" : self.role_id,
            "admin" : self.admin,
            "support_id" : self.support_id
        }


class Database():
    """
    user_data : {
        user_id : int,
        exp : int,
        money : int,
        voice : int #minutes,
        messages : int,
        custom_text : str,
        inventory : array,
        custom_roles : array
    }

    channel_data : {
        channel_id : int
    }
    """
    def __init__(self, database):
        self.connect(database)
    
    def connect(self, database_):
        Cluster = MongoClient("mongodb+srv://user:o0NFJeLOdfIaDaKD@cluster0.qbwbb.mongodb.net/serverdb?retryWrites=true&w=majority")
        database = Cluster["userstates"]
        self.db = database[database_]
        print("Connected to database")
    
    def get_user(self, user_id):
        """
        input{
            user_id : int
        }
        output{
            user_data ? user_data : dict
        }
        return user_data or create if not exists
        """
        user_data = self.db.find_one({"user_id" : user_id})
        if not user_data is None:
            return user_data
        else:
            return self.create_user(user_id)
    
    def create_user(self, user_id):
        """
        input{
            user_id : int
        }
        output{
            user_data
        }
        return created user_data
        """
        user = User(user_id).raw()
        self.db.insert_one(user)
        return user
    
    def remove_user(self, user_id):
        """
        input{
            user_id : int
        }
        return delete_one() result
        """
        return self.db.delete_one({'user_id' : user_id})

    
    def update_user(self, user_id, mode = "set", **keys):
        """
        input{
            user_id : int,
            mode : set or increment,
            keys : params what will be changed and new value
        }
        output{
            user_data ? user_data : dict || None
        }
        return updated user_data
        """
        user_data = self.db.find_one({"user_id" : user_id})
        if not user_data is None:
            res = self.db.update_one({"user_id" : user_id}, {f"${mode}" : keys})
            return res.raw_result
        else:
            return None
    
    def get_top(self):
        """
        output{
            top_users : dict
        }
        return the users who have the biggest params
        """
        money = self.db.find_one(sort = [("money", -1)])
        exp = self.db.find().sort([("exp", -1)]).limit(1)
        voice = self.db.find().sort([("voice", -1)]).limit(1)
        messages = self.db.find().sort([("messages", -1)]).limit(1)
        print(money)
        if not (money or exp or voice or messages):
            return None
        else:
            return {
                "money" : money["user_id"],
                "exp" : exp["user_id"],
                "voice" : voice["user_id"],
                "messages" : messages["user_id"]
            }
    
    def add_channel(self, channel_id, role_id = None, admin_id = None, support_id = None):
        """
        input{
            channel_id : int
        }
        output{
            channel_data
        }
        return created channel_data
        """
        channel = Voice_Channel(channel_id, role_id, admin_id, support_id).raw()
        self.db.insert_one(channel)
        return channel
    
    def get_channel(self, channel_id):
        """
        input{
            channel_id : int
        }
        output{
            channel_data
        }
        return channel_data
        """
        channel = self.db.find_one({"channel_id" : channel_id})
        return channel
    
    def get_all_channels(self):
        return list(self.db.find({}))
    
    def remove_channel(self, channel_id):
        """
        input{
            channel_id : int
        }
        output{
            channel_data
        }
        return delete_one() result
        """
        channel = self.db.delete_one({"channel_id" : channel_id})
        return channel
