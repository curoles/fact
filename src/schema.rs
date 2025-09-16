use yaml_schema::{RootSchema, Context, Validator};
use saphyr::LoadableYamlNode;

pub fn validate_yaml(yaml_str_to_validate: &str) -> Result<(), Box<dyn std::error::Error>> {
    let root_schema = RootSchema::load_from_str(include_str!("schema.yaml"))?;
    let yaml_schema = root_schema.schema.as_ref();
    let schema = yaml_schema.schema.as_ref().unwrap();
    let docs = saphyr::MarkedYaml::load_from_str(yaml_str_to_validate)?;
    let value = docs.first().expect("empty yaml");
    let context = Context::with_root_schema(&root_schema, true);
    let result = schema.validate(&context, value);
    assert!(result.is_ok());
    if context.has_errors() {
        println!("Error: {:?}", context.errors);
    }
    assert!(!context.has_errors());
    Ok(result?)
}

