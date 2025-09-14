//use std::fs;
use std::path;
use std::env;

//https://github.com/chyh1990/yaml-rust/blob/master/examples/dump_yaml.rs
//use yaml_rust::{YamlLoader, Yaml};//, yaml};

use crate::kg::{Node, Graph};
use crate::display::CliDisplay;

mod kg;
mod display;

fn main() {

    let args: Vec<_> = env::args().collect();

    if args.len() < 2 {
        println!("Provide path to KG files. Exit App.");
        return
    }
    
    let kg_path = path::Path::new(args[1].as_str());
    let _ok = Graph::load_files(kg_path, kg_path);

    let ok = Graph::check().expect("Error while checking graph");
    println!("Memory footprint: {} bytes", Graph::get_memory_footprint());
    
    if !ok {
        println!("Graph is broken. Exit App.");
        return
    }
    
    let dsp = CliDisplay;
        
    if args.len() > 2 {
        let node_name = args[2].as_str();
        Graph::display_node(&dsp, node_name);    
    }
}



/*#[allow(dead_code)]
fn process_fact(fact_name: &str, data: &Yaml)
{
    println!("{:?}", data);
    println!("{:?}", data[fact_name]);
    //let fact_map: &yaml::Hash = data.into();
    //for (k, v) in *data {
    //    println!("{:?} -> {:?}", k, v);
    //}
}*/