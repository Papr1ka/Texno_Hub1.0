import inspect
from discord.ext.commands import errors


class InvalidArgumentError(errors.BadArgument):
    def __init__(self, param : str):
        super().__init__('{0} is an invalid.'.format(param))

class UserError(InvalidArgumentError):
	def __init__(self, param):
		self.param = inspect.Parameter(param, inspect.Parameter.KEYWORD_ONLY)
		super().__init__(self.param)

class InvalidItemError(InvalidArgumentError):
    def __init__(self):
        super(InvalidItemError, self).__init__("Item")

class InvalidRoleError(InvalidArgumentError):
    def __init__(self):
        super(InvalidRoleError, self).__init__("Role")

class InvalidNameError(InvalidArgumentError):
    def __init__(self):
        super(InvalidNameError, self).__init__("Name")

class InvalidColorError(InvalidArgumentError):
    def __init__(self):
        super(InvalidColorError, self).__init__("Color")

class InvalidFriendError(InvalidArgumentError):
    def __init__(self):
        super(InvalidFriendError, self).__init__("SecondMember")

class InvalidArgError(InvalidArgumentError):
    def __init__(self):
        super(InvalidArgError, self).__init__(f"Arg")

class NotEnoughMoneyError(UserError):
    def __init__(self, value):
        super(NotEnoughMoneyError, self).__init__(f"TheUserHasNotGotEnoughMoney{value}")

class HasNoRequiredRole(UserError):
    def __init__(self):
        super(HasNoRequiredRole, self).__init__(f"TheUserHasNotGotRequiredRole")

class InvalidBetError(UserError):
    def __init__(self):
        super(InvalidBetError, self).__init__(f"TheUserBetIsIncorrect")

class InvalidSimpleBetError(UserError):
    def __init__(self):
        super(InvalidSimpleBetError, self).__init__(f"TheUserBetIsIncorrect")

class InvalidMoneyError(UserError):
    def __init__(self):
        super(InvalidMoneyError, self).__init__(f"TheInvalidMoneyError")

class NotConnectedError(UserError):
    def __init__(self):
        super(NotConnectedError, self).__init__(f"TheUserIsNotConnected")

class NotPrivateChannelError(UserError):
    def __init__(self):
        super(NotPrivateChannelError, self).__init__(f"TheUserChannelIsNotPrivate")

class NotChannelAdminError(UserError):
    def __init__(self):
        super(NotChannelAdminError, self).__init__(f"TheUserIsNotChannelAdmin")
