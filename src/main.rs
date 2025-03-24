use std::fs;
use std::env;
use yaml_rust::{YamlLoader};//, yaml};

//https://github.com/chyh1990/yaml-rust/blob/master/examples/dump_yaml.rs


fn main() {

    //let args: Vec<_> = env::args().collect();
    println!("Hello, world!");

    let path = env::current_dir().expect("Can't show current directory");
    println!("The current directory is {}", path.display());

    let fact_name = "string";
    let file_name = format!("db/{fact_name}.yaml");

    assert!(fs::exists(&file_name).expect("Can't find file"));

    let file_contents: String = fs::read_to_string(file_name).expect("Can't read file");

    let docs = YamlLoader::load_from_str(&file_contents).unwrap();
    let data = &docs[0];

    println!("{:?}", data);
    println!("{:?}", data[fact_name]);
    //let fact_map: &yaml::Hash = data.into();
    //for (k, v) in *data {
    //    println!("{:?} -> {:?}", k, v);
    //}
}
