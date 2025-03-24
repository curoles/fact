use std::fs;
use std::path;
use std::env;
use yaml_rust::{YamlLoader};//, yaml};

//https://github.com/chyh1990/yaml-rust/blob/master/examples/dump_yaml.rs


fn main() {

    let args: Vec<_> = env::args().collect();

    let path = env::current_dir().expect("Can't show current directory");
    println!("The current directory is {}", path.display());

    let fact_name = if args.len() <= 1 {"string"} else {args[1].as_str()};

	println!("Fact name is '{}'", fact_name);
    let search_path = if args.len() <= 2 {None} else {Some(args[2].as_str())};
	find_fact_file(fact_name, search_path);

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

fn find_fact_file(fact_name: &str, path_option: Option<&str>) -> Option<path::PathBuf> {
    let search_path =
    match path_option {
        None => {
            let current_path = env::current_dir().expect("Can't get current directory");
            current_path.to_str().unwrap().to_owned() + "/db"
        }
        Some(path_str) => {
            path_str.to_string()
        }
    };
    println!("Search in '{}'", search_path);

    for entry in fs::read_dir(search_path).ok()? {
        let entry = entry.ok()?;
        let path = entry.path();

        let metadata = fs::metadata(&path).ok()?;
        //println!("{:?}", path);
        if metadata.is_file() {
            let file_name = path.file_name().ok_or("No filename").ok()?;
            //println!("{:?}", file_name);
            let file_name = file_name.to_str()?;
            let file_name_n = &file_name[..fact_name.len()];
            //println!("{:?}", file_name_n);
            if file_name_n == fact_name {
                println!("Found file for '{}' in {:?}", fact_name, path);
                return Some(path);
            }
        }
    }

    return None;
}
