package dao;

import java.util.List;
import model.Product;

public class ProductDao {
    public List<Product> findAllProducts() {
        return sqlSession.select("ProductMapper.findAllProducts");
    }

    public Product findProductById(int id) {
        return sqlSession.select("ProductMapper.findProductById", id);
    }

    public void insertProduct(Product product) {
        sqlSession.insert("ProductMapper.insertProduct", product);
    }
}
