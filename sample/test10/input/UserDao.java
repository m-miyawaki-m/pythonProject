public class UserDao {
    public void getUserById(int id) {
        sqlSession.selectOne("UserMapper.getUserById", id);
    }

    public void insertUser(String name, int age) {
        sqlSession.insert("UserMapper.insertUser", new User(name, age));
    }
}
