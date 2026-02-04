const dbsToClean = ['Yukki', 'MukeshRobot', 'MUK_chats', 'MUK_users', 'waifu_mgmt'];
const migrations = [
    { from: 'Yukki', to: 'waifuversemusic' },
    { from: 'MukeshRobot', to: 'waifuversemgmt' }
];

migrations.forEach(m => {
    print(`Migrating ${m.from} to ${m.to}...`);
    const sourceDB = db.getSiblingDB(m.from);
    sourceDB.getCollectionNames().forEach(c => {
        sourceDB.getCollection(c).aggregate([{ $out: { db: m.to, coll: c } }]);
    });
});

dbsToClean.forEach(d => {
    print(`Dropping ${d}...`);
    db.getSiblingDB(d).dropDatabase();
});

print('\nCleanup Complete. Databases now on VPS:');
db.adminCommand({ listDatabases: 1 }).databases.forEach(d => {
    if (!['admin', 'config', 'local'].includes(d.name)) {
        print(` - ${d.name}`);
    }
});
