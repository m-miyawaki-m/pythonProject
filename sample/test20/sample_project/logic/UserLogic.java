package logic;

import dao.UserDao;
import model.User;

public class UserLogic {
    private UserDao userDao = new UserDao();

    public List<User> getAllUsers() {
        return userDao.findAllUsers();
    }

    public User getUserById(int id) {
        return userDao.findUserById(id);
    }

    public void addUser(User user) {
        userDao.insertUser(user);
    }
}
