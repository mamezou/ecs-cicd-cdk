# CDK V2を使用したECS FargateへのAmazon CI/CDパイプライン
_完全なDevOps対応のコンテナ化されたサンプルアプリケーション_

このプロジェクトは、Fargate、ECS、CodeBuild、CodePipelineを使用して、AWS上で公開可能な完全なコンテナ化されたFlaskアプリケーションのサンプルを構築し、新しいアプリケーションに変更を継続的にロールアウトする完全に機能するパイプラインを作成します。

## はじめに

[Cloud 9]() の使用を推奨しますが、独自の開発マシンを使用することもできます。その場合、jq、npm、AWS CDK、AWS CLI、Typescriptなどの基本要件をインストールするコマンドを調整する必要があります。


### Cloud9環境のセットアップ

`t2.micro` [Cloud9 us-east-1](https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines) ターミナルを起動し、次のコマンドで準備します:

```bash
sudo yum install -y jq
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bash_profile
echo "export AWS_REGION=${AWS_REGION}" | tee -a ~/.bash_profile
aws configure set default.region ${AWS_REGION}
aws configure get default.region
```

Cloud9インスタンスに管理者ロールが割り当てられていることを確認し、Cloud9 -> AWS設定 -> 認証情報 -> 一時的な認証情報を無効にします。

CDKの前提条件を準備します:

```bash
sudo yum install -y npm
npm install -g aws-cdk
npm install -g typescript@latest
```

次に、AWSアカウントが設定されていることを確認します。`aws configure`を実行するか、`AWS_ACCESS_KEY`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`環境変数が正しく設定されていることを確認してください。

### GitHubリポジトリの設定とアプリケーションのアップロード

https://github.com/aws-samples/amazon-ecs-fargate-cdk-v2-cicd を開きます。
GitHubにログインし、リポジトリを自分のアカウントにフォークします。

Cloud9環境にアクセスし、`~/environment`ディレクトリから次のコマンドを実行します（USER-NAMEをあなたのGitHubユーザー名に置き換えてください）。 

```bash
git clone https://github.com/USER-NAME/amazon-ecs-fargate-cdk-v2-cicd.git 
```

### GitHubトークンのシークレットを作成する

セキュリティのベストプラクティスとして、GitHubトークンをコードにハードコードしないでください。AWS Secrets Managerサービスを使用してGitHubトークンを保存し、CDK APIを使用してコードからトークンにアクセスします。

#### GitHubでパーソナルアクセストークンを作成する
GitHubのウェブサイトから、Settings/Developer Settings/Personal access tokensに移動し、次の権限を持つ新しいトークンを作成します:

* admin:repo_hook
* admin:org_hook
* repo

ウィンドウはまだ閉じないでください。次のステップでトークンの値が必要になります。

#### AWS Secrets Managerにトークンを保存する

デフォルトでは、このシークレットの名前は 
`/aws-samples/amazon-ecs-fargate-cdk-v2-cicd/github/personal_access_token` です。

シークレット名を変更するには、以下で適切に置換を行い、[`cdk deploy ステップ`](#aws-cloud-developement-kit-cdk-を使用したインフラストラクチャの起動)でオプションの`githubTokenSecretName`パラメータを指定してください。

```bash
aws configure set region $AWS_REGION
aws secretsmanager create-secret \
 --name /aws-samples/amazon-ecs-fargate-cdk-v2-cicd/github/personal_access_token \
 --secret-string <GITHUB-TOKEN> 
```

上記のコマンドを実行したら、次のコマンドを使用してシークレットが期待通りに保存されているか確認します:

```bash
aws secretsmanager get-secret-value \
 --secret-id /aws-samples/amazon-ecs-fargate-cdk-v2-cicd/github/personal_access_token \
 --version-stage AWSCURRENT
```

### CodeBuildを認証する

Code Pipelineを通じてデプロイをトリガーするGitHubフックを作成するため、CodeBuildを承認する必要があります。
次のスニペットで<GITHUB-TOKEN>をGitHubパーソナルアクセストークンに置き換え、開発環境で実行してください。

```bash
aws codebuild import-source-credentials \
 --server-type GITHUB \
 --auth-type PERSONAL_ACCESS_TOKEN \
 --token <GITHUB-TOKEN> 
```

認証情報のインポートが成功したか確認します。

```bash
aws codebuild list-source-credentials 
```

### AWS Cloud Developement Kit (CDK) を使用したインフラストラクチャの起動

クローンしたリポジトリの`cdk-v2`ディレクトリに移動し、次のコマンドを実行します:

```bash
cd amazon-ecs-fargate-cdk-v2-cicd/cdk-v2
cdk init
npm install
npm run build
cdk ls
cdk bootstrap aws://$ACCOUNT_ID/$AWS_REGION
```


次に、アプリケーションの合成とデプロイを行います:

```bash
cdk synth
cdk deploy \
 --parameters githubUserName=<myGithubUserName>
```

CloudFormationが実行される前に、ロールと承認の作成を確認するよう求められる場合があります。その場合は「Y」で応答してください。インフラストラクチャの作成には約5〜10分かかります。ターミナルにCloudFormationの出力が表示されるまでお待ちください。

次のようにデプロイのパラメータを制御することもできます:

```bash
cdk deploy \
 --parameters githubUserName=<myGithubUserName>\
 --parameters githubPersonalTokenSecretName="<myGithubPersonalTokenSecretName>" \
 --parameters datadogApiKey="<myDatadogApiKey>" \
 --context stackName="<myStackName>"
 ```

### インフラストラクチャとアプリケーションの確認


CloudFormationのデプロイが完了したら、CDK出力からURLを取得します。これはAWSウェブコンソールでも確認できます。

<img src="images/stack-launch.png" />

最初は、アプリはここで定義され、ECSタスク定義に追加された基本イメージを表します
[./cdk-v2/lib/ecs_cdk-stack.ts](/cdk-v2/lib/ecs_cdk-stack.ts#L87):

```typescript
const container = taskDef.addContainer('flask-app', {
    image: ecs.ContainerImage.fromRegistry("public.ecr.aws/amazonlinux/amazonlinux:2022"),
    memoryLimitMiB: 256,
    cpu: 256,
    logging
});
```

これが、最初にアプリのURLをクリックするとエラーページが表示される理由です。


CodePipelineがトリガーされると、CodeBuildは[./flask-docker-app](./flask-docker-app)フォルダにあるアプリケーションをDockerize化し、Amazon ECRリポジトリにプッシュする一連のコマンドを実行します。
ECSインフラストラクチャにデプロイする前に、次のステージに進むための手動承認を求められます。
承認されると、タスク定義、サービスを作成し、希望する数のタスクをインスタンス化して、アプリケーションをECSプラットフォームにデプロイします。このケースでは、デフォルトの希望数は1であり、したがって、上記のようにロードバランサーからflaskアプリケーションのインスタンスにアクセスできます。

ECSへの最初のデプロイには、古いアプリケーションタスクが正常にドレインされ、新しいタスクが起動することを確認するため、約5分かかります。ECSサービスが定常状態（下図）に達すると、アプリケーションにアクセスできるようになります。また、希望数に達していることにも注意してください。

<img src="images/ecs-steadystate.png" alt="dashboard" style="border:1px solid black">

ALB経由でアプリケーションにアクセスすると、コンテンツは以下の画像に更新されます:

<img src="images/ecs-deployed.png" alt="dashboard" style="border:1px solid black">

コードがコミットされCodePipelineが開始されると、アプリケーションがFargateにデプロイされます。CI/CDパイプラインの正常な実行は以下のようになります:

<img src="images/stage12-green.png" alt="dashboard" style="border:1px solid black">
<img src="images/stage34-green.png" alt="dashboard" style="border:1px solid black">

## 次のステップ

スタックがデプロイされると、コードの変更を素早く反復できるようになり、新しいバージョンが自動的にビルドされステージングされます。承認されると、そのバージョンがライブにプッシュされます。


## ライセンス
このライブラリはMIT-0ライセンスの下でライセンスされています。詳細は[LICENSE](/LICENSE)ファイルを参照してください。
