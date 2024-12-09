/*
 * UserLogic.java
 */
@Service
public class UserLogic {
    @Autowired
    private UserDAO userDAO;

    public User fetchUserById(int id) {
        return userDAO.getUserById(id); // Logic: fetchUserById -> DAO: getUserById
    }

    public void addUser(String name, String email) {
        userDAO.insertUser(name, email); // Logic: addUser -> DAO: insertUser
    }
}