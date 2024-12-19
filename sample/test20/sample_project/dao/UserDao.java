package dao;

import java.util.List;
import model.User;

public class UserDao {
    public List<User> findAllUsers() {
        return sqlSession.select("UserMapper.findAllUsers");
    }

    public User findUserById(int id) {
        return sqlSession.select("UserMapper.findUserById", id);
    }

    public void insertUser(User user) {
        sqlSession.insert("UserMapper.insertUser", user);
    }
}
