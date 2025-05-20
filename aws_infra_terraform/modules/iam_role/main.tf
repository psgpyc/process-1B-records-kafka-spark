resource "aws_iam_role" "this" {
    name = var.iam_role_name
    assume_role_policy = var.assume_role_policy_
    
}

resource "aws_iam_policy" "this" {
    name = "${var.iam_role_name}-policy"
    policy = var.i_am_policy_

}

resource "aws_iam_role_policy_attachment" "this" {
    role = aws_iam_role.this.name
    policy_arn = aws_iam_policy.this.arn
  
}

