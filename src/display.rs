use crate::Node;

pub trait KgDisplay {
    fn no_node(&self, node_name: &str);
    fn node(&self, node: &Node);
}

pub struct CliDisplay;

impl KgDisplay for CliDisplay {

    fn no_node(&self, node_name: &str) {
        println!("Node {} does not exist", node_name);
    }

    fn node(&self, node: &Node) {
        println!("{:?}", node.name);
    }

}
