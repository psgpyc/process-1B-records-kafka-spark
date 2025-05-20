module "create_iam_role" {
    source = "./modules/iam_role"
    iam_role_name = "psgpyc-allow-s3-role"
    assume_role_policy_ = file("./policies/assume_role_policy.json")
    i_am_policy_ = file("./policies/i_am_policy.json") 
    
}