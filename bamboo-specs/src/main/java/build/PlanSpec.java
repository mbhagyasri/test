package build;

import com.atlassian.bamboo.specs.api.BambooSpec;
import com.atlassian.bamboo.specs.api.builders.BambooKey;
import com.atlassian.bamboo.specs.api.builders.deployment.Environment;
import com.atlassian.bamboo.specs.api.builders.permission.PermissionType;
import com.atlassian.bamboo.specs.api.builders.permission.Permissions;
import com.atlassian.bamboo.specs.api.builders.permission.PlanPermissions;
import com.atlassian.bamboo.specs.api.builders.plan.Job;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.PlanIdentifier;
import com.atlassian.bamboo.specs.api.builders.plan.Stage;
import com.atlassian.bamboo.specs.api.builders.plan.artifact.Artifact;
import com.atlassian.bamboo.specs.api.builders.plan.branches.BranchCleanup;
import com.atlassian.bamboo.specs.api.builders.plan.branches.PlanBranchManagement;
import com.atlassian.bamboo.specs.api.builders.project.Project;
import com.atlassian.bamboo.specs.api.builders.requirement.Requirement;
import com.atlassian.bamboo.specs.builders.task.CheckoutItem;
import com.atlassian.bamboo.specs.builders.task.InjectVariablesTask;
import com.atlassian.bamboo.specs.builders.task.ScriptTask;
import com.atlassian.bamboo.specs.builders.task.VcsCheckoutTask;
import com.atlassian.bamboo.specs.builders.trigger.BitbucketServerTrigger;
import com.atlassian.bamboo.specs.model.task.InjectVariablesScope;
import com.atlassian.bamboo.specs.model.task.ScriptTaskProperties;
import com.atlassian.bamboo.specs.util.BambooServer;
import com.atlassian.bamboo.specs.api.builders.plan.branches.BranchIntegration;
import com.atlassian.bamboo.specs.api.builders.plan.PlanBranchIdentifier;
import com.atlassian.bamboo.specs.api.builders.deployment.Deployment;
import com.atlassian.bamboo.specs.api.builders.task.AnyTask;
import com.atlassian.bamboo.specs.api.builders.permission.EnvironmentPermissions;
import com.atlassian.bamboo.specs.api.builders.deployment.ReleaseNaming;
import com.atlassian.bamboo.specs.api.builders.permission.DeploymentPermissions;
import com.atlassian.bamboo.specs.builders.task.ArtifactDownloaderTask;
import com.atlassian.bamboo.specs.builders.task.CleanWorkingDirectoryTask;
import com.atlassian.bamboo.specs.builders.task.DownloadItem;
import com.atlassian.bamboo.specs.util.MapBuilder;
import com.atlassian.bamboo.specs.api.builders.Variable;
import com.atlassian.bamboo.specs.api.builders.AtlassianModule;
import com.atlassian.bamboo.specs.builders.trigger.AfterSuccessfulBuildPlanTrigger;
//YAML stuff
import java.io.*;
import com.amihaiemil.eoyaml.*;
import java.io.IOException;

/**
 * Plan configuration for Bamboo.
 * Learn more on: <a href="https://confluence.atlassian.com/display/BAMBOO/Bamboo+Specs">https://confluence.atlassian.com/display/BAMBOO/Bamboo+Specs</a>
 */
@BambooSpec
public class PlanSpec {
    ///////////////////////CONSTANTS////////////////////////
    public static String SERVER_NAME = "https://bamboo.cdk.com";

    public static String GIT_REPO = "athena-app-cmdb";

    public static String PROJECT_NAME = "Athena Platform";
    public static String PROJECT_KEY = "NGIP";

    public static String PLAN_NAME = PlanSpec.GIT_REPO+"-spec";
    public static String PLAN_KEY = "CMDB";
    //PERMISSIONS
    public static String GROUP_NAME = "Athena PCP";

    //ENVIROMENTS
    //DEV
    public static String ENV_DEV_NAME = "us-dev";
    public static String ENV_DEV_VAR = "./enviroments/dev/vars.yml";
    //NONPROD
    public static String ENV_NONPROD_NAME = "us-nonprod";
    public static String ENV_NONPROD_VAR = "./enviroments/nonprod/vars.yml";
    //PROD
    public static String ENV_PROD_NAME = "us-prod";
    public static String ENV_PROD_VAR = "./enviroments/prod/vars.yml";

    public static String ENV_TASK = "docker run \\\n"+
    "-e AWS_ACCESS_KEY_ID=${bamboo.AWS_ACCESS_KEY_ID_SECRET} \\\n"+
    "-e AWS_SECRET_ACCESS_KEY=${bamboo.AWS_SECRET_ACCESS_KEY} \\\n"+
    "-e AWS_DEFAULT_REGION=${bamboo.AWS_DEFAULT_REGION} \\\n"+
    "-e IQR_ENVIRONMENT=${bamboo.IQR_ENVIRONMENT} \\\n"+
    "-e EKS_CLUSTER_NAME=${bamboo.EKS_CLUSTER_NAME} \\\n"+
    "-e BAMBOO_SECRET=${bamboo.BAMBOO_SECRET} \\\n"+
    "-e BAMBOO_BUILD_ID=${bamboo.artifact.container_tag} \\\n"+
    "artifactory.cdk.com/docker-local/athena/athena-platform/athena-app-cmdb-install:${bamboo_artifact_container_tag}";

    /*
     * Run main to publish plan on Bamboo
     */
    public static void main(final String[] args) throws Exception { 
        BambooServer bambooServer = new BambooServer(PlanSpec.SERVER_NAME);

        Plan plan = new PlanSpec().createPlan();
        bambooServer.publish(plan);

        Deployment deployment = new PlanSpec().createDeployment();
        bambooServer.publish(deployment);

        //Permissions for plan and deployment
        PlanPermissions planPermission = new PlanSpec().createPlanPermission(plan.getIdentifier());
        bambooServer.publish(planPermission);
        DeploymentPermissions deploymentPermission = new PlanSpec().createDeploymentPermission();
        bambooServer.publish(deploymentPermission);

        //Enviroment permissions
        //dev
        EnvironmentPermissions envPermission1 = new PlanSpec().createEnvironmentPermission1();
        bambooServer.publish(envPermission1);
        //nonprod
        EnvironmentPermissions envPermission2 = new PlanSpec().createEnvironmentPermission2();
        bambooServer.publish(envPermission2);
        //prod
        EnvironmentPermissions envPermission3 = new PlanSpec().createEnvironmentPermission3();
        bambooServer.publish(envPermission3);

    }

    PlanPermissions createPlanPermission(PlanIdentifier planIdentifier) {
        Permissions permission = new Permissions()
                .groupPermissions(PlanSpec.GROUP_NAME, PermissionType.BUILD, PermissionType.VIEW, PermissionType.EDIT, PermissionType.ADMIN)
                .groupPermissions("Athena Platform Developers", PermissionType.BUILD, PermissionType.VIEW, PermissionType.EDIT, PermissionType.ADMIN)
                .loggedInUserPermissions(PermissionType.VIEW);
        return new PlanPermissions(planIdentifier.getProjectKey(), planIdentifier.getPlanKey()).permissions(permission);
    }

    DeploymentPermissions createDeploymentPermission() {
        Permissions permission = new Permissions()
                    .groupPermissions(PlanSpec.GROUP_NAME, PermissionType.VIEW, PermissionType.EDIT)
                    .groupPermissions("Athena Platform Developers", PermissionType.VIEW, PermissionType.EDIT)
                    .loggedInUserPermissions(PermissionType.VIEW);
        return new DeploymentPermissions(PlanSpec.PLAN_NAME).permissions(permission);
    }
    //ENVIROMENT PERMISSIONS
    //DEV
    EnvironmentPermissions createEnvironmentPermission1() {
        Permissions permission = new Permissions()
                    .groupPermissions(PlanSpec.GROUP_NAME, PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .groupPermissions("Athena Platform Developers", PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .loggedInUserPermissions(PermissionType.VIEW);
        return new EnvironmentPermissions(PlanSpec.PLAN_NAME).permissions(permission).environmentName(PlanSpec.ENV_DEV_NAME);
    }
    //NONPROD
    EnvironmentPermissions createEnvironmentPermission2() {
        Permissions permission = new Permissions()
                    .groupPermissions(PlanSpec.GROUP_NAME, PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .groupPermissions("Athena Platform Developers", PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .loggedInUserPermissions(PermissionType.VIEW);
        return new EnvironmentPermissions(PlanSpec.PLAN_NAME).permissions(permission).environmentName(PlanSpec.ENV_NONPROD_NAME);
    }
    //PROD
    EnvironmentPermissions createEnvironmentPermission3() {
        Permissions permission = new Permissions()
                    .groupPermissions(PlanSpec.GROUP_NAME, PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .groupPermissions("Athena Platform Developers", PermissionType.VIEW, PermissionType.EDIT, PermissionType.BUILD)
                    .loggedInUserPermissions(PermissionType.VIEW);
        return new EnvironmentPermissions(PlanSpec.PLAN_NAME).permissions(permission).environmentName(PlanSpec.ENV_PROD_NAME);
    }

    Project project() {
        return new Project()
                .name(PlanSpec.PROJECT_NAME)
                .key(PlanSpec.PROJECT_KEY);
    }
    ///////////////////////BUILD PLAN///////////////////////
    Plan createPlan() {
        return new Plan(
                project(),
                PlanSpec.PLAN_NAME, PlanSpec.PLAN_KEY)
                .description("Plan created from spec respository:"+PlanSpec.GIT_REPO)
                .linkedRepositories(PlanSpec.GIT_REPO)
                .stages(
                    new Stage("Build")
                    .jobs(new Job("Build Job", "JOB1")
                        .artifacts(new Artifact()
                                .name("artifact")
                                .copyPattern(".artifact")
                                .shared(true))
                        .tasks(
                            new VcsCheckoutTask()
                                    .description("Source code checkout")
                                    .checkoutItems(new CheckoutItem().defaultRepository())
                                    .cleanCheckout(true),
                            new ScriptTask()
                                .interpreter(ScriptTaskProperties.Interpreter.BINSH_OR_CMDEXE)
                                .inlineBody("export container_tag=${bamboo.buildNumber}\nsh bamboo-specs/scripts/build.sh --verbose\n"),
                            new InjectVariablesTask()
                                .path(".artifact")
                                .namespace("artifact")
                                .scope(InjectVariablesScope.RESULT))
                        .requirements(new Requirement("system.docker.executable"))))
                        .triggers(new BitbucketServerTrigger())
                        .planBranchManagement(new PlanBranchManagement()
                            .createForPullRequest()
                            .delete(new BranchCleanup()
                                .whenRemovedFromRepositoryAfterDays(1))
                            .branchIntegration(new BranchIntegration()
                                .integrationBranch(new PlanBranchIdentifier(new BambooKey(PlanSpec.PLAN_KEY))))
                        .notificationLikeParentPlan());
    }
    ///////////////////////ENVIROMENTS///////////////////////
    //DEV
    Environment dev(){
        return new Environment(PlanSpec.ENV_DEV_NAME)
        .triggers(new AfterSuccessfulBuildPlanTrigger()
        .description("Build"))
        .tasks(
            new CleanWorkingDirectoryTask(),
            new ArtifactDownloaderTask()
            .description("Download release contents")
            .artifacts(new DownloadItem()
                .artifact("artifact")),
            new AnyTask(new AtlassianModule("com.atlassian.bamboo.plugin.requirementtask:task.requirements"))
            .configuration(new MapBuilder()
                        .put("existingRequirement", "system.docker.executable")
                        .put("regexMatchValue", "")
                        .put("requirementKey", "")
                        .put("requirementMatchType", "exist")
                        .put("requirementMatchValue", "")
                        .build()),
            new ScriptTask()
                .description("Install")
                .interpreter(ScriptTaskProperties.Interpreter.BINSH_OR_CMDEXE)
                .inlineBody(PlanSpec.ENV_TASK))
            .variables(
                fillVars(PlanSpec.ENV_DEV_VAR)
            )
        .requirements(new Requirement("system.docker.executable"));
    }
    //NONPROD
    Environment nonprod(){
        return new Environment(PlanSpec.ENV_NONPROD_NAME)
        .triggers(new AfterSuccessfulBuildPlanTrigger()
        .description("Build"))
        .tasks(
            new CleanWorkingDirectoryTask(),
            new ArtifactDownloaderTask()
            .description("Download release contents")
            .artifacts(new DownloadItem()
                .artifact("artifact")),
            new AnyTask(new AtlassianModule("com.atlassian.bamboo.plugin.requirementtask:task.requirements"))
            .configuration(new MapBuilder()
                        .put("existingRequirement", "system.docker.executable")
                        .put("regexMatchValue", "")
                        .put("requirementKey", "")
                        .put("requirementMatchType", "exist")
                        .put("requirementMatchValue", "")
                        .build()),
            new ScriptTask()
                .description("Install")
                .interpreter(ScriptTaskProperties.Interpreter.BINSH_OR_CMDEXE)
                .inlineBody(PlanSpec.ENV_TASK))
            .variables(
                fillVars(PlanSpec.ENV_NONPROD_VAR)
            )
        .requirements(new Requirement("system.docker.executable"));
    }
    //PROD
    Environment prod(){
        return new Environment(PlanSpec.ENV_PROD_NAME)
        .tasks(
            new CleanWorkingDirectoryTask(),
            new ArtifactDownloaderTask()
            .description("Download release contents")
            .artifacts(new DownloadItem()
                .artifact("artifact")),
            new AnyTask(new AtlassianModule("com.atlassian.bamboo.plugin.requirementtask:task.requirements"))
            .configuration(new MapBuilder()
                        .put("existingRequirement", "system.docker.executable")
                        .put("regexMatchValue", "")
                        .put("requirementKey", "")
                        .put("requirementMatchType", "exist")
                        .put("requirementMatchValue", "")
                        .build()),
            new ScriptTask()
                .description("Install")
                .interpreter(ScriptTaskProperties.Interpreter.BINSH_OR_CMDEXE)
                .inlineBody(PlanSpec.ENV_TASK))
            .variables(
                fillVars(PlanSpec.ENV_PROD_VAR)
            )
        .requirements(new Requirement("system.docker.executable"));
    } 
    ///////////////////////DEPLOYMENT///////////////////////

    Deployment createDeployment(){
        return new Deployment(
            new PlanIdentifier(PlanSpec.PROJECT_KEY, PlanSpec.PLAN_KEY),
            PlanSpec.PLAN_NAME)
        .releaseNaming(new ReleaseNaming("${bamboo.artifact.container_tag}"))
        .environments(dev(),nonprod(),prod());
    }

    ///////////////////////YAML///////////////////////
    public int returnLines(String path){//gets amoutn ofl ines in config to determien array lenghts
        int lines = 0;
        try{
            //get lines
            BufferedReader reader = new BufferedReader(new FileReader (path));
            while (reader.readLine() != null) lines++;
            reader.close();
        }catch (IOException ex){
            System.out.println("no data");
        }
        return lines;
    }

    public Variable[] fillVars(String path){//create atalasian variable array for enviromental vars
        int size = returnLines(path);
        File yaml = new File(path);
        String [] key_list = new String[size];
        String [] val_list = new String[size];
        Variable[] varArray = new Variable[size];

        try{
            YamlMapping yaml_data = Yaml.createYamlInput(yaml).readYamlMapping();
            String keys = yaml_data.keys().toString();
            //Cleanup keys list and convert to array
            key_list = keys.replace("\n", "").replace("---", "").replace("...", "")
            .replace("[", "").replace("]", "").replace(" ", "").split(",");
            //get yaml data
            for(int i=0; i<size; i++){
                val_list[i] = yaml_data.string(key_list[i]);
            }
        }catch (IOException ex){
        }

       for (int i=0; i<size; i++) {
            varArray[i] = new Variable(key_list[i],val_list[i]);
        }
        return varArray;
    }

}
