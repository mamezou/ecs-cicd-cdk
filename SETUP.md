# セットアップガイド

このガイドでは、FastAPIアプリケーションをAWS ECS Fargateにデプロイし、AWS CodePipelineを使用したCI/CDパイプラインを構築する手順を説明します。

## 📋 前提条件

### 既に設定済みであること

- ✅ **AWS SSOアクセス**: 組織のAWS SSOにログインできること
- ✅ **GitHubアカウント**: リポジトリをフォーク・プッシュできること

### ローカル環境にインストール済みであること

- ✅ [Node.js](https://nodejs.org/) 18以上
- ✅ [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- ✅ [Git](https://git-scm.com/)

### インストール確認

```bash
node --version  # v18以上
aws --version   # 2.x以上
git --version
```

## 🚀 セットアップ手順（30分）

### 1. AWS SSOログイン

既存のSSOプロファイルを使用してログイン:

```bash
# SSOログイン
aws sso login --profile <your-sso-profile>

# プロファイルを環境変数に設定
export AWS_PROFILE=<your-sso-profile>

# 確認
aws sts get-caller-identity
```

> **Note**: AWS SSOの設定方法は [docs/AWS_SSO_SETUP.md](./docs/AWS_SSO_SETUP.md) を参照（既に設定済みの場合は不要）

### 2. リポジトリのフォークとクローン

```bash
# 1. GitHub上でこのリポジトリをフォーク（ブラウザで操作）

# 2. フォークしたリポジトリをクローン
git clone https://github.com/<your-username>/ecs-cicd-cdk.git
cd ecs-cicd-cdk

# 3. 依存関係のインストール
npm install
npm run build
```
