public class UserLogic {
    public void getUser() {
        getUserDao();
    }

    public void createUser() {
        UserDao userDao = new UserDao();
        userDao.insertUser("John", 25);
    }

    public void getUserDao() {
        UserDao userDao = new UserDao();
        userDao.getUserById(1);
    }
}
