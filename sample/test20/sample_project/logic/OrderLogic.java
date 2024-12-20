package logic;

import dao.ProductDao;
import model.Product;

public class OrderLogic {
    private ProductDao productDao = new ProductDao();

    public List<Product> getAllProducts() {
        return productDao.findAllProducts();
    }

    public Product getProductById(int id) {
        return productDao.findProductById(id);
    }

    public void addProduct(Product product) {
        productDao.insertProduct(product);
    }
}
