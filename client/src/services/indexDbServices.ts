const DB_NAME = "bridge-db";
const DB_VERSION = 1;

// Object represantantion of indexedDb objectStores
const STORES = [
	{
		name: "message",
		indexes: [
			{ name: "conversationId", unique: false },
			{ name: "status", unique: false },
		],
	},
	{
		name: "friends",
		indexes: [
			{ name: "userName", unique: true },
			{ name: "email", unique: true },
		],
	},
	{
		name: "conversation",
		indexes: [{ name: "participant", unique: true }],
	},
	{
		name: "tempFile",
	},
];

class IndexedDbService {
	private db: IDBDatabase | null = null;
	private newlyCreated = false;

	async openDb(): Promise<void> {
		if (!window.indexedDB) {
			console.error("IndexedDb is not supported by your brouser");
			return;
		}

		return new Promise<void>((resolve, rejects) => {
			const request: IDBOpenDBRequest = window.indexedDB.open(
				DB_NAME,
				DB_VERSION
			);

			request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
				this.newlyCreated = true;
				const db = (event.target as IDBOpenDBRequest).result;

				STORES.forEach((storeName) => {
					if (!db.objectStoreNames.contains(storeName.name)) {
						const store = db.createObjectStore(storeName.name, {
							keyPath: "id",
							autoIncrement: false,
						});

						storeName.indexes?.forEach((index) => {
							if (!store.indexNames.contains(index.name)) {
								store.createIndex(index.name, index.name, {
									unique: index.unique,
								});
							}
						});
					}
				});
			};

			request.onsuccess = () => {
				this.db = request.result;
				resolve();
			};

			request.onerror = () => {
				rejects(request.error);
			};
		});
	}

	async addRecord(storeName: string, data: object): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			const transaction = this.db.transaction(storeName, "readwrite");
			const store = transaction.objectStore(storeName);

			const request = store.add(data);

			request.onsuccess = () => {
				// console.log(request?.result);
				resolve(request.result);
			};

			request.onerror = () => {
				rejects(data);
			};
		});
	}

	async updateRecord(storeName: string, data: object): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			const transaction = this.db.transaction(storeName, "readwrite");
			const store = transaction.objectStore(storeName);

			const request = store.put(data);

			request.onsuccess = () => {
				// console.log(request?.result);
				resolve(request.result);
			};

			request.onerror = () => {
				rejects(data);
			};
		});
	}

	async getRecord(
		storeName: string,
		id: string | null,
		indexes?: { [key: string]: string }
	): Promise<object> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<object>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			const transaction = this.db.transaction(storeName, "readonly");
			const store = transaction.objectStore(storeName);

			if (id) {
				const storeRequest = store.get(id);
				storeRequest.onsuccess = () => {
					resolve(storeRequest.result);
				};

				storeRequest.onerror = () => {
					rejects(storeRequest.error);
				};
			} else if (indexes) {
				const storeIndexes = store.index(Object.keys(indexes)[0]);
				const storeRequest = storeIndexes.get(
					indexes[Object.keys(indexes)[0]]
				);

				storeRequest.onsuccess = () => {
					resolve(storeRequest.result);
				};
				storeRequest.onerror = () => {
					rejects(storeRequest.error);
				};
			} else {
				rejects(new Error("No id or valid argument"));
			}
		});
	}

	async getAllRecords(
		storeName: string,
		index?: { [key: string]: string }
	): Promise<{ newlyCreated: boolean; objects: object[] }> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<{
			newlyCreated: boolean;
			objects: object[];
		}>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			//open a transaction in indesedDb
			const transaction = this.db.transaction(storeName, "readonly");
			const store = transaction.objectStore(storeName);

			if (index) {
				//retrive an index object and search for the given value
				const storeIndexes = store.index(Object.keys(index)[0]);
				const request = storeIndexes.openCursor(
					IDBKeyRange.only(index[Object.keys(index)[0]])
				);

				const results: object[] = [];

				request.onsuccess = (event) => {
					// store the result of current cursor, store in relusts and push the cursor forwored
					const cursor = (event.target as IDBRequest).result;

					if (cursor) {
						results.push(cursor.value);
						cursor.continue();
					} else {
						resolve({
							newlyCreated: this.newlyCreated,
							objects: results,
						});
					}
				};
				request.onerror = () => {
					rejects(request.error);
				};
			} else {
				// get all the objects and return the value
				const request = store.getAll();

				request.onsuccess = () => {
					resolve({
						newlyCreated: this.newlyCreated,
						objects: request.result,
					});
				};

				request.onerror = () => {
					rejects(request.error);
				};
			}
		});
	}

	async deleteRecord(
		storeName: string,
		key: string
	): Promise<{ objectId: string }> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<{ objectId: string }>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			const transaction = this.db.transaction(storeName, "readwrite");
			const store = transaction.objectStore(storeName);

			const request = store.delete(key);

			request.onsuccess = () => {
				resolve({ objectId: key });
			};

			request.onerror = () => {
				rejects(request.error);
			};
		});
	}

	async batchUpsert(storeName: string, data: object[]): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error("Database is not open."));
				return;
			}

			const transaction = this.db.transaction(storeName, "readwrite");
			const store = transaction.objectStore(storeName);

			const result: IDBValidKey[] = [];
			let errorOccurred = false;

			data.forEach((record) => {
				const request = store.put(record);

				request.onsuccess = (event: Event) => {
					const key = (event.target as IDBRequest).result;
					result.push(key);
				};

				request.onerror = (event: Event) => {
					console.error(
						"Failed to insert record:",
						(event.target as IDBRequest).error
					);
					errorOccurred = true;
				};
			});

			transaction.oncomplete = () => {
				if (errorOccurred) {
					rejects(new Error("Some records failed to insert."));
				} else {
					resolve(result);
				}
			};

			transaction.onerror = () => {
				rejects(result);
			};
		});
	}

	async clearDatabase() {
		const dbRequest = indexedDB.deleteDatabase(DB_NAME);
		dbRequest.onerror = () => console.error("Error deleting database");
		dbRequest.onsuccess = () =>
			console.log("Database deleted successfully");
	}
}

export const indexedDbService = new IndexedDbService();
