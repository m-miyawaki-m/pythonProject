public interface UserDAO {
    User getUserById(@Param("id") int id);  // id: getUserById
    void insertUser(@Param("name") String name, @Param("email") String email);  // id: insertUser
}